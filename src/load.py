import shutil
import stat
from pathlib import Path
from typing import List

import src.params as params


def load_data(
    data_source: str,
    data_destination: str = params.raw_folder,
    allowed_extensions: List[str] = [".csv"],
) -> None:
    """

    Parameters
    ----------
    data_source : str
        The data directory to load the data from.
    data_destination : str, optional
        The name of the folder to save data to
        The default is raw_folder.
    allowed_extensions : List[str], optional
        Allowed extensions to raw data.
        The default is [".csv"].

    Returns
    -------
    None.

    """

    destination_path = Path.cwd().joinpath("data", data_destination)
    source_path = Path(data_source)

    # fetch all files
    for file in list(source_path.iterdir()):
        if file.is_file() and file.suffix in allowed_extensions:
            # construct full file path
            destination = destination_path.joinpath(file.name)
            shutil.copyfile(file, destination)
            Path.chmod(destination, stat.S_IWRITE)  # make sure location allows write
            print("copied", file.name)
