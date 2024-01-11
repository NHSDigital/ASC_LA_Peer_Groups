from datetime import date

import pandas as pd
import pytest

from src.utils import (
    check_121_mappings,
    check_file_for_duplicates,
    get_unique_folder_name,
    random_string,
)


def test_random_string():

    for length in [5, 10]:
        string_1 = random_string(length)
        string_2 = random_string(length)

        assert string_1 != string_2
        assert len(string_1) == length
        assert len(string_2) == length


def test_unique_folder_name():

    for length in [5, 10]:
        name_1 = get_unique_folder_name(length)
        name_2 = get_unique_folder_name(length)

        assert name_1 != name_2

        assert len(name_1) == length + 20  # length of datetime
        assert len(name_2) == length + 20

        date_today = date.today().strftime("%d-%m-%Y")

        assert (name_1[0:10]) == date_today
        assert (name_2[0:10]) == date_today


def test_check_for_duplicates():
    duped_data = [["01", "A"], ["02", "A"], ["02", "B"]]
    duped_df = pd.DataFrame(duped_data, columns=["test_lsoa_code", "test_la_code"])
    with pytest.raises(ValueError):
        check_file_for_duplicates(duped_df, "test_file", "test_lsoa_code")


def test_check_121_mappings():
    multiple_maps_data = [["01", "A"], ["01", "B"], ["02", "B"]]
    multiple_maps_df = pd.DataFrame(
        multiple_maps_data, columns=["test_lsoa_code", "test_la_code"]
    )
    with pytest.raises(ValueError):
        check_121_mappings(
            multiple_maps_df, "test_file", "test_lsoa_code", "test_la_code"
        )
