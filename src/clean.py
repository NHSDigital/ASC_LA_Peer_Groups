from pathlib import Path
from typing import Dict, List

import pandas as pd

import src.params as params
from src.utils import check_121_mappings, check_file_for_duplicates

DATA = Path(params.data_folder)
RAW_DATA = DATA.joinpath(params.raw_folder)
INTERIM_DATA = DATA.joinpath(params.interim_folder)


def remove_wales_lsoas(
    df: pd.DataFrame, lsoa_field_name: str = params.LSOA_code
) -> pd.DataFrame:
    """
    Filters out LSOAs that are within Wales.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing all LSOAs.
    lsoa_field_name : str, optional
        The LSOA code to use, e.g. "LSOA22CD".
        The default is params.LSOA_code.

    Returns
    -------
    df_england : pd.DataFrame
        DataFrame with only England LSOAs.

    """
    df_england = df[df[lsoa_field_name].str.startswith("E")].copy()

    return df_england


def clean_distance_to_sea(
    raw_file: str = params.distance_to_sea_file,
    column_name: str = params.distance_to_sea,
) -> None:
    """
    Cleans distance to sea file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The name of the distance to sea file.
        Defaults to params.distance_to_sea_file.
    column_name: str, optional
        Name to use for column of interest.
        Defaults to params.distance_to_sea

    Returns
    -------
    None.

    """
    distance_to_sea = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))

    distance_to_sea.rename(columns={"distance to sea km": column_name}, inplace=True)

    distance_to_sea = remove_wales_lsoas(distance_to_sea)
    distance_to_sea.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Distance to sea has been cleaned and saved")

    return None


def clean_lookups(
    la_code: str,
    la_name: str,
    las_to_remove: List[str],
    lsoa_utla_file: str = params.LSOA_UTLA_lookup_file,
    lsoa_code: str = params.LSOA_code,
) -> None:
    """
    Cleans lookups and saves a clean copy.

    Parameters
    ----------
    la_code : str
        Local authority column code to use. E.g. "UTLA22CD"
    la_name : str
        Local authority column name to use. E.g. "UTLA22NM"
    las_to_remove: List[str]
        Local authorities to remove from lookup
    lsoa_utla_file : str, optional
        File name containing LSOA to UTLA lookup.
        The default is params.LSOA_UTLA_lookup_file.
    lsoa_code: str
        The lsoa code to use. E.g. "LSOA21CD"

    Returns
    -------
    None
    """
    LSOA_UTLA_lookup = pd.read_csv(
        Path(RAW_DATA).joinpath(lsoa_utla_file),
        usecols=[lsoa_code, la_code, la_name],
    )

    check_file_for_duplicates(
        df=LSOA_UTLA_lookup, file_name=lsoa_utla_file, col=lsoa_code
    )

    for left, right in {lsoa_code: la_name, la_code: la_name, la_name: la_code}.items():
        check_121_mappings(
            df=LSOA_UTLA_lookup,
            file_name=lsoa_utla_file,
            left_field=left,
            right_field=right,
        )

    if las_to_remove:  # check if array is empty
        for la in las_to_remove:
            if la in LSOA_UTLA_lookup[la_name].values:
                print(f"Removing {la} from look up")
                LSOA_UTLA_lookup = LSOA_UTLA_lookup[LSOA_UTLA_lookup[la_name] != la]
            else:
                print(f"WARNING - {la} does not exist, please check config")

    LSOA_UTLA_lookup.to_csv(
        Path(INTERIM_DATA).joinpath(f"{lsoa_utla_file}"),
        index=False,
    )

    print("LSOA UTLA Lookup has been cleaned and saved")

    return None


def clean_ethnicity(
    raw_file: str = params.ethnicity_data_file,
    columns_to_keep: Dict[str, List[str]] = params.ethnic_group_cols_to_keep,
) -> None:
    """
    Cleans ethnicity file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw ethnicity file name.
        The default is params.ethnicity_data_file.
    columns_to_keep : Dict[str, List[str]], optional
        The ethnicity columns to keep.
        The default is params.ethnic_group_cols_to_keep.

    Returns
    -------
    None.

    """

    ethnicity_df = pd.read_csv(
        Path(RAW_DATA).joinpath(raw_file), usecols=list(columns_to_keep.values())
    )
    ethnicity_df.rename(
        columns={v: k for k, v in columns_to_keep.items()}, inplace=True
    )
    ethnicity_df = remove_wales_lsoas(ethnicity_df)
    ethnicity_df.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Ethnicity data has been cleaned and saved")

    return None


def clean_population_data(
    raw_file: str = params.population_data_file,
    area_file: str = params.area_file,
) -> None:
    """
    Cleans population data file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        the raw population file name.
        The default is params.population_data_file.
    area_file : str, optional
        The LSOA to area file name.
        The default is params.area_file.

    Returns
    -------
    None.

    """
    pop_data = pd.read_csv(Path(RAW_DATA).joinpath(raw_file), header=0)
    area_data = pd.read_csv(
        Path(RAW_DATA).joinpath(area_file),
        usecols=[params.LSOA_code, params.area_sq_km],
    )

    pop_data[params.over_15_population] = pop_data[params.pop_columns_to_add].sum(
        axis=1
    )
    pop_data[params.age_65_to_84_population] = pop_data[
        params.pop_columns_to_add[10:14]
    ].sum(axis=1)

    pop_data = pop_data.rename(
        columns={
            params.ethnicity_geo_col: params.LSOA_code,
            params.over_85_population_original_name: params.over_85_population,
        }
    )
    # Calculate population density at LSOA for sparsity calculation
    pop_data = pop_data.merge(area_data, on=params.LSOA_code, how="inner")
    pop_data[params.pop_density_lsoa_column] = (
        pop_data[params.total_population] / pop_data[params.area_sq_km]
    )

    pop_data = pop_data[
        [
            params.LSOA_code,
            params.total_population,
            params.over_15_population,
            params.age_65_to_84_population,
            params.over_85_population,
            params.pop_density_lsoa_column,
            params.area_sq_km,
        ]
    ]

    pop_data = remove_wales_lsoas(pop_data)
    pop_data.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Population Data has been saved")

    return None


def clean_english_proficiency(
    raw_file: str = params.english_proficiency_data_file,
) -> None:
    """
    Cleans english proficiency file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw english proficiency file name.
        The default is params.english_proficiency_data_file.

    Returns
    -------
    None.

    """
    english_df = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))

    english_df = english_df[
        ["geography code", params.eng_prof_total] + params.eng_prof_low
    ].copy()
    english_df[params.processed_eng_prof_low] = english_df[params.eng_prof_low].sum(
        axis=1
    )
    english_df.rename(
        columns={
            "geography code": params.LSOA_code,
            params.eng_prof_total: params.processed_eng_prof_total,
        },
        inplace=True,
    )
    english_df.drop(columns=params.eng_prof_low, inplace=True)
    english_df = remove_wales_lsoas(english_df)
    english_df.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("English proficiency data has been cleaned and saved")

    return None


def clean_housing_tenure(raw_file: str = params.housing_tenure_data_file) -> None:
    """
    Cleans housing tenure file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw housing tenure file name.
        The default is params.housing_tenure_data_file.

    Returns
    -------
    None.

    """
    housing_df = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))

    housing_df = housing_df[
        [
            "geography code",
            params.housing_tenure_total,
            params.housing_tenure_ownership,
            params.housing_tenure_social_rent,
        ]
    ].copy()
    housing_df.rename(
        columns={
            "geography code": params.LSOA_code,
            params.housing_tenure_total: params.processed_tenure_total,
            params.housing_tenure_ownership: params.processed_owners,
            params.housing_tenure_social_rent: params.processed_renters,
        },
        inplace=True,
    )
    housing_df = remove_wales_lsoas(housing_df)
    housing_df.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Housing tenure data has been cleaned and saved")

    return None


def clean_qualification_level(
    raw_file: str = params.qualification_level_data_file,
) -> None:
    """
    Cleans qualification file and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw qualification data file name.
        The default is params.qualification_level_data_file.

    Returns
    -------
    None.

    """
    qual_level = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))

    qual_level = qual_level[
        [
            "geography code",
            params.qual_level_total,
            params.higher_qual_level,
        ]
    ].copy()
    qual_level.rename(
        columns={
            "geography code": params.LSOA_code,
            params.qual_level_total: params.processed_qual_level_total,
            params.higher_qual_level: params.processed_qual_level_higher,
        },
        inplace=True,
    )
    qual_level = remove_wales_lsoas(qual_level)
    qual_level.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Qualifications data has been cleaned and saved")

    return None


def clean_nssec(
    raw_file: str = params.nssec_data_file,
) -> None:
    """
    Cleans nssec data and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw nssec file name.
        The default is params.nssec_data_file.

    Returns
    -------
    None.

    """
    nssec_df = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))

    nssec_df = nssec_df[
        ["geography code", params.nssec_total, params.nssec_student]
        + params.nssec_routine_manual_occupations
    ].copy()
    nssec_df[params.processed_routine_manual] = nssec_df[
        params.nssec_routine_manual_occupations
    ].sum(axis=1)
    nssec_df.rename(
        columns={
            "geography code": params.LSOA_code,
            params.nssec_total: params.processed_nssec_total,
            params.nssec_student: params.processed_nssec_student,
        },
        inplace=True,
    )
    nssec_df.drop(columns=params.nssec_routine_manual_occupations, inplace=True)
    nssec_df = remove_wales_lsoas(nssec_df)
    nssec_df.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("NS-SEC data has been cleaned and saved")

    return None


def clean_rooms(
    raw_file: str = params.rooms_file, room_limit: int = params.room_limit
) -> None:
    """
    Cleans the number of rooms files and saves a clean copy.

    Parameters
    ----------
    raw_file : str, optional
        The raw room file name.
        The default is params.rooms_file.
    room_limit : int, optional
        The maximum number of rooms, houses with less rooms are counted.
        The default is params.room_limit.

    Returns
    -------
    None.

    """
    rooms_df = pd.read_csv(Path(RAW_DATA).joinpath(raw_file))
    rooms_dict = {
        col: col.replace(params.rooms_col_prefix, "")
        for col in rooms_df
        if col.startswith(params.rooms_col_prefix)
    }
    n_rooms_dict = {
        old_col: int(n_rooms[0])
        for old_col, n_rooms in rooms_dict.items()
        if not n_rooms.startswith("Total")
    }
    few_room_cols = [
        col for col in n_rooms_dict.keys() if n_rooms_dict[col] < room_limit
    ]
    rooms_df[params.few_rooms] = rooms_df[few_room_cols].sum(axis=1)

    rooms_df.rename(
        columns={
            "geography code": params.LSOA_code,
            f"{params.rooms_col_prefix}{params.rooms_total}": "total",
        },
        inplace=True,
    )
    rooms_df.drop(columns=n_rooms_dict.keys(), inplace=True)
    rooms_df = remove_wales_lsoas(rooms_df)
    rooms_df.to_csv(
        Path(INTERIM_DATA).joinpath(f"{raw_file}"),
        index=False,
    )

    print("Rooms data has been cleaned and saved")
    return None


def clean_all(la_code: str, la_name: str, las_to_remove: List[str]) -> None:
    """
    A wrapper function that cleans all the raw data by calling functions in this file.

    Parameters
    ----------
    la_code : str
        Local authority column code to use. E.g. "UTLA22CD"
    la_name : str
        Local authority column name to use. E.g. "UTLA22NM"
    las_to_remove:
        Local authorities to remove from lookup.

    Returns
    -------
    None

    """
    clean_lookups(la_code=la_code, la_name=la_name, las_to_remove=las_to_remove)

    clean_distance_to_sea()

    clean_ethnicity()

    clean_population_data()

    clean_nssec()

    clean_english_proficiency()

    clean_housing_tenure()

    clean_qualification_level()

    clean_rooms()

    return None
