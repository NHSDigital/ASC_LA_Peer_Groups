# AGGREGATION

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

import src.params as params

DATA = Path(params.data_folder)
INTERIM_DATA = DATA.joinpath(params.interim_folder)
PRIMARY_DATA = DATA.joinpath(params.primary_folder)


def calculate_sparsity(input_file: str, la_keys: List[str], write_output: bool = True):
    """
    Calculates the sparsity for each LSOA and saves an aggregated version.

    Parameters
    ----------
    input_file : str
        The population data file.
    la_keys : List[str]
        The local authority keys to use. E.g. ["UTLA22CD", "UTLA22NM"]
    write_output : bool, optional
        If true, save as a csv file.
        The default is True.

    Returns
    -------
    df_sparsity
        The aggregated sparsity dataframe.

    """
    df = join_to_utla(input_file)
    df["density_per_hectare"] = df[params.pop_density_lsoa_column] / 100
    df_super_sparse = df[df["density_per_hectare"] <= 0.5]
    df_sparse = df[(df["density_per_hectare"] > 0.5) & (df["density_per_hectare"] <= 4)]

    def _sparsity_agg(df: pd.DataFrame, name: str):
        df_agg = df.groupby(la_keys)[params.total_population].sum()
        df_agg.rename(name, inplace=True)
        return df_agg

    df_total = df.groupby(la_keys)[params.total_population].sum()
    df_super_sparse = _sparsity_agg(df_super_sparse, "super_sparse") * 2
    df_sparse = _sparsity_agg(df_sparse, "sparse")
    df_total = pd.merge(
        df_total, df_super_sparse, left_index=True, right_index=True, how="left"
    )
    df_total = pd.merge(
        df_total, df_sparse, left_index=True, right_index=True, how="left"
    )
    df_total.fillna({"sparse": 0, "super_sparse": 0}, inplace=True)
    df_total[params.sparsity] = (
        df_total["sparse"] / df_total[params.total_population]
    ) + (df_total["super_sparse"] / df_total[params.total_population])
    df_sparsity = df_total[params.sparsity]
    if write_output:
        df_sparsity.to_csv(
            Path(PRIMARY_DATA).joinpath(params.sparsity_file), index=True
        )
    print("sparsity.csv aggregated and saved")
    return df_sparsity


def join_to_utla(
    input_file: str,
    lsoa_version: str = params.LSOA_code,
    look_up_file: str = params.LSOA_UTLA_lookup_file,
):
    """
    Joins UTLAs to LSOAs.

    Parameters
    ----------
    input_file : str
        File name containing a column of LSOAs.
    lsoa_version : str, optional
        The LSOA code field to use, i.e. "LSOA22CD"
        The default is params.LSOA_code.
    look_up_file : str, optional
        Which lookup file name to use.
        The default is params.lookup_file.

    Returns
    -------
    file_with_utla : pd.DataFrame.

    """
    look_up_file = INTERIM_DATA.joinpath(look_up_file)

    file = pd.read_csv(
        Path(INTERIM_DATA).joinpath(f"{input_file}"),
        # usecols=columns_to_agg + [lsoa_version],
    )
    lookup = pd.read_csv(look_up_file)
    file_with_utla = file.merge(lookup, on=lsoa_version, how="inner")

    return file_with_utla


def agg_to_local_authority(
    input_file: str,
    la_keys: List[str],
    columns_to_agg: list,
    division_map: Optional[Dict[str, List[str]]] = None,
    cols_to_drop: Optional[List[str]] = None,
    agg_type: str = "sum",
    write_output: bool = False,
) -> pd.DataFrame:
    """
    Aggregates LSOA data from an input file to local authority level.

    Parameters
    ----------
    input_file : str
        File name with data broken down by LSOA.
    la_keys : List[str]
        The local authority keys to use. E.g. ["UTLA22CD", "UTLA22NM"]
    columns_to_agg : list
        The columns you would like to use during aggregation,
        either as numerators or denominators.
    division_map : Optional[Dict[str, List[str]]], optional
        A dictionary specifying the denominator for each feature used during
        aggregation.
        To work out the indian population percentage, one would use the division map:
        {"total" : ["indian population"]}
        Where "total" is the name of the denominator column and "indian population"
        is the numerator column.
        For multiple numerators with the same denominator, use a division map like:
        {"total" : ["indian population", "bangladeshi population"]}
        Where "total" is again the denominator.
        And "indian population" and "bangladeshi population" are both numerator columns.
        The default is None.
    cols_to_drop : Optional[List[str]], optional
        Columns you would like to drop after aggregation.
        The default is None.
    agg_type : str, optional
        Aggregate calculation that only accepts some possible values.
        Possible values: ["sum","mean"].
        The default is "sum".
    write_output : bool
        If true, write a csv file.
        The default is False.

    Returns
    -------
    file_agg: pd.DataFrame
        The aggregated file.

    """
    file_with_utla = join_to_utla(input_file)

    if agg_type == "sum":
        file_agg = file_with_utla.groupby(la_keys)[columns_to_agg].sum()
    elif agg_type == "mean":
        file_agg = file_with_utla.groupby(la_keys)[columns_to_agg].mean()

    if division_map is not None:
        for denominator_col, numerator_cols in division_map.items():
            for col in numerator_cols:
                if denominator_col == params.area_sq_km:
                    file_agg[col] = file_agg[col].div(file_agg[denominator_col])
                    file_agg = file_agg.rename(columns={col: params.pop_density_column})
                else:
                    file_agg[col] = file_agg[col].div(file_agg[denominator_col]) * 100
                    file_agg = file_agg.rename(columns={col: f"{col} %"})

    if cols_to_drop is not None:
        file_agg.drop(columns=cols_to_drop, inplace=True)

    if write_output:
        file_agg.to_csv(Path(PRIMARY_DATA).joinpath(f"{input_file}"), index=True)

    print(f"{input_file} aggregated and saved")

    return file_agg


def aggregate_all(la_keys: List[str], write_sub_output: bool = False):
    """
    Aggregates all columns by calling functions within this file.

    Parameters
    ----------
    la_keys : List[str]
        The local authority keys to use. E.g. ["UTLA22CD", "UTLA22NM"]
    write_sub_output : bool, optional
        If true, write singular files to csv.
        The default is False.

    Returns
    -------
    None.

    """
    population = agg_to_local_authority(
        input_file=params.population_data_file,
        la_keys=la_keys,
        columns_to_agg=[
            params.over_15_population,
            params.age_65_to_84_population,
            params.over_85_population,
            params.total_population,
            params.area_sq_km,
        ],
        division_map={
            params.over_15_population: [
                params.age_65_to_84_population,
                params.over_85_population,
            ],
            params.area_sq_km: [params.total_population],
        },
        cols_to_drop=[params.area_sq_km],
        write_output=write_sub_output,
    )

    population_sparsity = calculate_sparsity(
        input_file=params.population_data_file,
        la_keys=la_keys,
        write_output=write_sub_output,
    )

    ethnicity = agg_to_local_authority(
        input_file=params.ethnicity_data_file,
        la_keys=la_keys,
        columns_to_agg=[
            col
            for col in params.ethnic_group_cols_to_keep.keys()
            if col != params.LSOA_code
        ],
        division_map={
            "total": [
                col
                for col in params.ethnic_group_cols_to_keep.keys()
                if col not in [params.LSOA_code, "total"]
            ]
        },
        cols_to_drop=["total"],
        write_output=write_sub_output,
    )

    housing = agg_to_local_authority(
        input_file=params.housing_tenure_data_file,
        la_keys=la_keys,
        columns_to_agg=[
            params.processed_tenure_total,
            params.processed_owners,
            params.processed_renters,
        ],
        division_map={
            params.processed_tenure_total: [
                params.processed_owners,
                params.processed_renters,
            ]
        },
        cols_to_drop=[params.processed_tenure_total],
        write_output=write_sub_output,
    )

    qualifications = agg_to_local_authority(
        input_file=params.qualification_level_data_file,
        la_keys=la_keys,
        columns_to_agg=[
            params.processed_qual_level_total,
            params.processed_qual_level_higher,
        ],
        division_map={
            params.processed_qual_level_total: [params.processed_qual_level_higher]
        },
        cols_to_drop=[params.processed_qual_level_total],
        write_output=write_sub_output,
    )

    english_proficiency = agg_to_local_authority(
        input_file=params.english_proficiency_data_file,
        la_keys=la_keys,
        columns_to_agg=[params.processed_eng_prof_low, params.processed_eng_prof_total],
        division_map={params.processed_eng_prof_total: [params.processed_eng_prof_low]},
        cols_to_drop=params.processed_eng_prof_total,
        write_output=write_sub_output,
    )

    nssec = agg_to_local_authority(
        input_file=params.nssec_data_file,
        la_keys=la_keys,
        columns_to_agg=[
            params.processed_nssec_student,
            params.processed_nssec_total,
            params.processed_routine_manual,
        ],
        division_map={
            params.processed_nssec_total: [
                params.processed_nssec_student,
                params.processed_routine_manual,
            ]
        },
        cols_to_drop=params.processed_nssec_total,
        write_output=write_sub_output,
    )

    rooms = agg_to_local_authority(
        input_file=params.rooms_file,
        la_keys=la_keys,
        columns_to_agg=[params.rooms_total_col, params.few_rooms],
        division_map={params.rooms_total_col: [params.few_rooms]},
        cols_to_drop=params.rooms_total_col,
        write_output=write_sub_output,
    )

    distance_to_sea = agg_to_local_authority(
        input_file=params.distance_to_sea_file,
        la_keys=la_keys,
        columns_to_agg=[params.distance_to_sea],
        agg_type="mean",
        write_output=write_sub_output,
    )

    aggregated = pd.concat(
        [
            population,
            population_sparsity,
            ethnicity,
            housing,
            english_proficiency,
            qualifications,
            nssec,
            rooms,
            distance_to_sea,
        ],
        axis=1,
    )

    aggregated.to_csv(Path(PRIMARY_DATA).joinpath("aggregated.csv"), index=True)

    print("All files aggregated and saved")
