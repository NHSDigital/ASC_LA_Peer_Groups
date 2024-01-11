import timeit
from typing import Optional

from src.clean import clean_all
from src.load import load_data
from src.model import calculate_distance, transform_data
from src.process import aggregate_all
from src.report import run_report
from src.utils import configure_pipeline, get_config, parse_cli_args


def main(custom_hash: Optional[str]):

    # load config
    config = get_config("config.toml")
    location = config["LOCATION"]
    la_code = config["LOCAL_AUTHORITY"]["la_code"]
    la_name = config["LOCAL_AUTHORITY"]["la_name"]
    n_la_peers = config["MODEL_OUTPUT"]["n_peers"]
    la_keys = [la_code, la_name]
    feature_weights = config["FEATURE_WEIGHTS"]
    remove_las = config["REMOVE_LAS"]["las_to_remove"]

    print(f"\n{'-'*60}\nPipeline starting\n")
    # Configure logging
    logger, folders = configure_pipeline(
        location["output_dir"],
        hash_length=location["hash_length"],
        custom_hash=custom_hash,
    )
    logger.info(f"Logging the config settings:\n\n\t{config}\n")
    # Create output folder
    print(f"\n{'-'*60}\nLoading Data\n")
    load_data(location["input_dir"])
    print(f"\n{'-'*60}\nCleaning Data\n")
    clean_all(la_name=la_name, la_code=la_code, las_to_remove=remove_las)
    print(f"\n{'-'*60}\nAggregating Data\n")
    aggregate_all(la_keys)
    print(f"{'-'*60}\nStarting Report\n")
    run_report(features=feature_weights, la_code=la_code, output_folders=folders)
    print(f"{'-'*60}\nStarting Transformations\n")
    df = transform_data(
        la_keys=la_keys,
        features=feature_weights,
        report=True,
        output_folders=folders,
    )
    print(f"{'-'*60}\nCalculating Euclidean Distance\n")
    calculate_distance(
        la_code=la_code, la_name=la_name, df=df, output_folders=folders, k=n_la_peers
    )


if __name__ == "__main__":
    args = parse_cli_args()
    custom_hash = args.hash
    print("Running create_publication script")
    start_time = timeit.default_timer()
    main(custom_hash)
    total_time = timeit.default_timer() - start_time
    total_minutes = int(total_time / 60)
    total_leftover_seconds = round(total_time % 60)
    print(
        f"""
        Running time of create_publication script:
        {total_minutes} minutes and {total_leftover_seconds} seconds.\n
        """
    )
