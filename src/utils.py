"""
Purpose of the script: configures logging
"""
import argparse
import logging
import os
import random
import shutil
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import toml

import src.params as params


def configure_pipeline(
    output_dir: str, hash_length: int, custom_hash: Optional[str] = None
) -> Tuple[logging.Logger, List[str]]:
    """Configure the pipeline run

    Parameters
    ----------
    output_dir : str
        Location to store outputs (including logs)
    hash_length : int
        Length of hash to use in pipeline folder
    custom_hash : Optional[str], optional
        Specify hash to use, by default None

    Returns
    -------
    Tuple[logging.Logger, List[str]]
        Logger object and output folders

    Raises
    ------
    ValueError
        If empty custom hash supplied
    """
    if custom_hash is not None:
        if len(custom_hash) == 0:
            raise ValueError("Custom hash must be of length > 0")
        if len(custom_hash) > hash_length:
            custom_hash = custom_hash[:hash_length]

    pipeline_hash = get_unique_folder_name(hash_length, custom_hash)
    logger = configure_logging(output_dir, pipeline_hash)

    output_folders = create_output_folder(output_dir, pipeline_hash)

    return (logger, output_folders)


def configure_logging(output_dir: str, hash_id: str) -> logging.Logger:
    """Set up logging format and location to store logs
    Store logs in a secure location (e.g. IC Green)
    Do not store logs on your local machine as they may contain traces of data.

    Args:
        output_dir: directory to store logs
        hash_id: pipeline hash

    Returns:
        (logging.Logger) logger to add detail to
    """
    log_folder = Path(output_dir).joinpath("logs")
    if not os.path.exists(Path(log_folder)):
        os.makedirs(Path(log_folder))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s -- %(filename)s:\
                %(funcName)5s():%(lineno)s -- %(message)s",
        handlers=[
            logging.FileHandler(log_folder / f"{hash_id}.log"),
            logging.StreamHandler(sys.stdout),
        ],  # Add second handler to print log message to screen
    )
    logger = logging.getLogger(__name__)

    logger.info("Configured logging.")
    logger.info(f"Run under hash: {hash_id}.")
    logger.info(f"Starting run at:\t{datetime.now().time()}")
    logger.info(f"Starting run at:\t{datetime.now().time()}")
    return logger


def get_config(toml_path="config.toml") -> dict:
    """Gets the config toml from the root directory and returns it as a dict.

    Returns:
        Dict: A dictionary containing details of the database, paths, etc.

    Example:
        from shmi_improvement.utilities.helpers import get_config
        config = get_config()
    """
    return toml.load(toml_path)


def random_string(length: int) -> str:
    """Generates a random string

    Args:
        length (int): The length of the string

    Returns:
        (str) A random string
    """
    pool = string.hexdigits
    return "".join(random.choice(pool) for i in range(length))


def get_unique_folder_name(length: int, custom_hash: Optional[str] = None) -> str:
    """Generates a unique folder name

    Args:
        length (int): Length of random hash
        custom_hash (Optional[str]): Custom hash to use

    Returns:
        str: A string containing a date and random, or custom hash.
    """
    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y_%H-%M-%S")

    if custom_hash is not None:
        print("Using custom hash")
        folder_string = f"{now_str}_{custom_hash}"
    else:
        folder_string = f"{now_str}_{random_string(length)}"

    return folder_string


def create_output_folder(output_path: str, output_folder: str):
    """Creates a new folder in the specified output path.

    Args:
        output_path (str):
            Location of output
        output_folder (str):
            Name of folder name to store pipeline run output

    Returns:
        list[str]: an array of paths
    """
    if not os.path.exists(Path(output_path)):
        os.makedirs(Path(output_path))

    project_output_path = Path(output_path).joinpath(output_folder)
    project_output_path_outputs = Path(project_output_path).joinpath(
        params.output_folder
    )
    project_output_path_reports = Path(project_output_path).joinpath(
        params.report_folder
    )
    project_output_path_transformations = Path(project_output_path).joinpath(
        params.transformations_folder
    )

    os.mkdir(project_output_path)
    os.mkdir(project_output_path_outputs)
    os.mkdir(project_output_path_reports)
    os.mkdir(project_output_path_transformations)

    print(f"Folders created in:\n{project_output_path}")

    shutil.copy2(
        src=(Path.cwd().joinpath("config.toml")),
        dst=project_output_path.joinpath("config.txt"),
    )
    print("Config copied and saved.")

    return [
        project_output_path,
        project_output_path_outputs,
        project_output_path_reports,
        project_output_path_transformations,
    ]


def copy_outputs(old_file_path: str, new_file_path: str, file_name: str) -> None:
    shutil.copy2(
        src=Path(old_file_path).joinpath(file_name),
        dst=Path(new_file_path).joinpath(file_name),
    )


def check_file_for_duplicates(df: pd.DataFrame, file_name: str, col: str) -> None:
    """Checks a field of a dataframe for duplicate values.
    The dataframe should contain data linked to a file.

    Args:
        df (pd.DataFrame):
            data from file
        file_name (str):
            name of file so that the user knows which file to check
        col (str):
            the field to check for duplicates

    Raises:
        ValueError if any col values appear more than once in the dataframe

    Returns:
        None
    """
    if df.duplicated(subset=[col]).any():
        raise ValueError(
            f"""Your dataset: {file_name} contains duplicate {col} values. \n
            This pipeline requires distinct {col} values."""
        )

    return None


def check_121_mappings(
    df: pd.DataFrame, file_name: str, left_field: str, right_field: str
) -> int:
    """Checks whether a field is mapped to more than one value in another field.
    The dataframe should contain data linked to a file.

    Args:
        df (pd.DataFrame):
            data from file
        file_name (str):
            name of file so that the user knows which file to check
        left_field (str):
            the field to map
        right_field (str):
            the field which may contain multiple values

    Raises:
        ValueError if left_field is mapped to more than one value of right_field

    Returns:
        None
    """
    df_count_mappings = df.groupby(left_field)[right_field].nunique()
    max_mapping = int(df_count_mappings.max())

    if max_mapping > 1:
        raise ValueError(
            f"""Your dataset: {file_name} contains incorrect mappings. \n
             It contains multiple {right_field} values for each {left_field}. \n
            This pipeline requires 1 {right_field} for each {left_field}"""
        )

    return None


def parse_cli_args() -> argparse.Namespace:
    """Parses arguments supplied at the command line

    Returns
    -------
    argparse.Namespace
        argparse object with hash attribute
    """
    parser = argparse.ArgumentParser(
        description="Pipeline to calculate Local Authority Peers"
    )
    parser.add_argument(
        "--hash", default=None, help="Supply a custom hash to store your pipeline."
    )
    args = parser.parse_args()
    return args
