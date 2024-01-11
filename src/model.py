import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import distance
from scipy.stats import boxcox, shapiro, yeojohnson
from sklearn import preprocessing

import src.params as params
from src.report import transformation_report

logger = logging.getLogger(__name__)

INPUT_PATH = Path(params.data_folder).joinpath(params.primary_folder)
OUTPUT_PATH = Path(params.output_folder)


def transform_data(
    la_keys: List[str],
    output_folders: list,
    features: Dict[str, float],
    report: bool = True,
    normalise: bool = True,
    custom_transformation: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Transforms the data for each feature using multiple methods.
    Tests which method is closest to a Gaussian.

    Parameters
    ----------
    la_keys : List[str]
        The local authority keys to use. E.g. ["UTLA22CD", "UTLA22NM"]
    output_folders: list,
        List containing 4 separate paths to the specified output folder.
    features : dict[str,float]
        A dictionary of the feature names and weights to to transform.
    report : bool, optional
        Create graphs to add to report.
        The default is True.
    normalise : bool, optional
        Ensure all values are between 0 and 1.
        The default is True.
    custom_transformation: dict[str,str], optional
        A dictionary overriding the 'best' method of transformation for each feature.
        The code for each transformation is:
            ''           - No Transformation
            'yj'         - Yeo johnson
            'sqrr'       - Square Root
            'log'        - log
            'squared'    - squared
            'bc'         - boxcox (values must be > 0)
            'recip_sqrr' - reciprocal square root (values must be > 0)
            'recip'      - reciprocal (values must be > 0)
        The default is None.

    Outputs
    -------
    Saves the values of each normalised and standardised feature for each UTLA.

    Returns
    -------
    transformed_data : Dataframe
       Dataframe containing all transformations to be used in Euclidean Distance.
    """
    df_all = pd.read_csv(Path(INPUT_PATH).joinpath(params.aggregated_file))
    # Initialise output
    transformed_output = df_all[la_keys].copy()

    for feature, weight in features.items():
        df_var = df_all[la_keys + [feature]].copy()

        if weight > 0:
            print(f"The weighting of {feature} is {weight}")
            transformed_data, greater_than_zero = _transform_var(df_var, feature)

            if normalise:
                transformed_data = _normalise_var(
                    transformed_data, weight, key_columns=la_keys
                )

            # Check how gaussian each column is
            transformed_data = _get_best_gaussian_transformation(
                transformed_data, feature, key_columns=la_keys
            )

            if report:
                OUT_TRANS = output_folders[3]
                transformation_report(
                    output=OUT_TRANS,
                    df=transformed_data,
                    feature=feature,
                    normalise=normalise,
                    greater_than_zero=greater_than_zero,
                )

            if custom_transformation is not None:
                if feature in custom_transformation.keys():
                    column_to_use = transformed_data[
                        la_keys + [f"{feature}_{custom_transformation[feature]}"]
                    ]
                else:
                    column_to_use = transformed_data[la_keys + [f"{feature}_best"]]
            else:
                column_to_use = transformed_data[la_keys + [f"{feature}_best"]]

            # Join the selected column to transformed data dataframe.
            transformed_output = transformed_output.merge(
                column_to_use,
                on=la_keys,
                how="inner",
            )

    for path in [output_folders[1], OUTPUT_PATH]:
        transformed_output.to_csv(Path(path).joinpath("features.csv"), index=False)

    return transformed_output


def _get_best_gaussian_transformation(
    df: pd.DataFrame, feature: str, key_columns: List[str]
) -> pd.DataFrame:
    """
    Finds feature transformation closest to a gaussian.

    Parameters
    -----------

        df : pd.dataframe
            Dataframe containing all transformations for one feature
        feature : str
            Column / feature name

    Returns:
        df : dataframe
            Dataframe with additional column containing closest transformation
            to a gaussian.
    """
    p_values = {
        column: shapiro(df[column]).pvalue
        for column in df.columns
        if column not in key_columns
    }
    max_p_col = max(p_values, key=p_values.get)

    df[f"{feature}_best"] = df[max_p_col]

    logger.info(f"The column closest to a gaussian is {max_p_col}")
    logger.info(f"With a P value of {p_values[max_p_col]}")

    return df


def _normalise_var(
    df: pd.DataFrame, weight: int, key_columns: List[str]
) -> pd.DataFrame:
    """
    Normalises a feature to a range between zero and a weight.

    Parameters
    -----------

        df : pd.dataframe
            Dataframe containing all transformations for one feature
        weight : int
            the maximum value a feature can be. e.g. 1.
        key_columns: List[str]
            List of column names that are keys.
            These columns do not need to be normalised

    Returns:
        df : dataframe
            Dataframe with transformations and weightings for one feature.
    """

    # get all values in column between 0 and specified weight
    for column in df.columns:
        if column not in key_columns:
            df[column] = preprocessing.MinMaxScaler(
                feature_range=(0, weight)
            ).fit_transform(np.array(df[column]).reshape(-1, 1))

    return df


def _transform_var(df: pd.DataFrame, feature: str) -> Tuple[pd.DataFrame, bool]:
    """
    Transforms the feature using multiple methods.

    Parameters
    ----------
    feature : str
        The name of the feature / column to transform.
    df : Dataframe
       Dataframe containing a feature to be transformed.

    Returns
    -------
    df : Dataframe
       Dataframe containing all transformations on one feature.
    greater_than_zero : bool
        If true, untransformed feature data contains zero values.

    """

    print(f"Transforming {feature}")

    # Check for 0s in data as this can impact transformations

    if df[feature].min() > 0:
        greater_than_zero = True
    else:
        greater_than_zero = False

    df[f"{feature}_yj"], lam = yeojohnson(df[feature])
    df[f"{feature}_sqrr"] = df[feature] ** 0.5
    df[f"{feature}_log"] = np.log1p(df[feature])
    df[f"{feature}_squared"] = df[feature] ** 2

    if greater_than_zero:
        df[f"{feature}_bc"], lam = boxcox(df[feature])
        df[f"{feature}_recip_sqrr"] = df[feature] ** -0.5
        df[f"{feature}_recip"] = 1 / df[feature]

    return df, greater_than_zero


def create_pairwise_distance_df(
    dist_matrix_df: pd.DataFrame, la_name: str, distance_col: str = "distance"
) -> pd.DataFrame:
    """
    Transforms a square matrix of distances into a 3 columns dataframe

    Parameters
    ----------
    df : pd.Dataframe
        The square matrix of euclidean distances between each local authority
    la_name : str
        The UTLA name to use. E.g. "UTLA22NM"
    distance_col : str, optional
        The name to give to the euclidean distance measurement
        The default is "distance"

    Outputs
    -------
    Saves the euclidean distance between every pair of local authorities.

    Returns
    -------
    A 3 column dataframe with each pair of local authorities compared to each other.
    Duplicates exist (i.e. the same pair is found in reverse).
    This in order to rank each.
    """
    # Transform square into 3 columns
    dist_matrix_reshaped = pd.DataFrame(dist_matrix_df.stack(), columns=[distance_col])

    dist_matrix_reshaped.index.names = [f"{la_name}_1", f"{la_name}_2"]
    dist_matrix_reshaped.reset_index(inplace=True)

    # Remove comparison to itself
    dist_matrix_reshaped = dist_matrix_reshaped[
        dist_matrix_reshaped[f"{la_name}_1"] != dist_matrix_reshaped[f"{la_name}_2"]
    ]

    dist_matrix_reshaped.sort_values(by=[f"{la_name}_1", distance_col], inplace=True)
    dist_matrix_reshaped.reset_index(drop=True, inplace=True)

    return dist_matrix_reshaped


def calculate_distance(
    df: pd.DataFrame,
    output_folders: list,
    la_code: str,
    la_name: str,
    k: int,
    distance_metric: str = "euclidean",
) -> None:
    """
    Calculates the Euclidean distance between each UTLA.

    Parameters
    ----------
    df : pd.Dataframe
        Contains the normalised and transformed features for each UTLA.
    output_folders: list,
        List containing 4 separate paths to the specified output folder.
    la_code : str
        The UTLA code to use. E.g. "UTLA22CD"
    la_name : str
        The UTLA name to use. E.g. "UTLA22NM"
    k : int, optional
        How many nearest neighbours to compute for each UTLA.

    Returns
    -------
    None.
    """

    print("Generating distances")

    # reorder columns for readability, save dataframe
    old_cols = [col for col in df.columns if col not in [la_code, la_name]]
    new_cols = [la_code, la_name] + old_cols
    df = df[new_cols]
    output = output_folders[1]

    dist_matrix = distance.pdist(df.drop(columns=[la_code, la_name]), distance_metric)
    dist_matrix = pd.DataFrame(
        distance.squareform(dist_matrix),
        index=df[la_name],
        columns=df[la_name],
    )

    # Save pairwise distances
    dist_matrix_reshaped = create_pairwise_distance_df(dist_matrix, la_name)
    for path in [output, OUTPUT_PATH]:
        dist_matrix_reshaped.to_csv(Path(path).joinpath("distances.csv"), index=False)

    print("Calculating top 10 nearest neighbours")

    n_nearest_neighbours_array = []
    for column in dist_matrix.columns:
        closest_distance = dist_matrix.nsmallest(k + 1, columns=column)
        # Find closest 10 euclidean distances, take the index
        closest_k = closest_distance[column].index[1:]
        output_row = closest_k.insert(0, column)
        n_nearest_neighbours_array.append(output_row)

    final_output = pd.DataFrame(
        n_nearest_neighbours_array,
        columns=[la_name] + [i for i in range(1, k + 1)],
    )

    example_10_output = final_output.loc[
        final_output[la_name].isin(params.example_utlas)
    ]

    for path in [output, params.output_folder]:
        final_output.to_csv(Path(path).joinpath("peers.csv"), index=False)
        example_10_output.to_csv(Path(path).joinpath("example_peers.csv"), index=False)

    print(f"Top {k} peers saved!! :) ")

    return None
