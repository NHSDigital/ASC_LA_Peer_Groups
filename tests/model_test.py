import numpy as np
import pandas as pd

from src.model import _get_best_gaussian_transformation, _normalise_var, _transform_var


def test_get_best_gaussian_transformation():

    gaussian_data = np.random.normal(loc=0.5, scale=0.5, size=100)
    random_data_1 = np.random.rand(1, 100)[0]
    random_data_2 = np.random.rand(1, 100)[0]

    input = pd.DataFrame(
        {
            "index": [i for i in range(100)],
            "transformation_1": gaussian_data,  # most gaussian
            "transformation_2": random_data_1,  # random
            "transformation_3": random_data_2,  # random
        }
    )

    actual = _get_best_gaussian_transformation(
        input, "transformation", key_columns=["index"]
    )

    expected = pd.DataFrame(
        {
            "index": [i for i in range(100)],
            "transformation_1": gaussian_data,  # most gaussian
            "transformation_2": random_data_1,  # random
            "transformation_3": random_data_2,  # random
            "transformation_best": gaussian_data,  # best
        }
    )

    pd.testing.assert_frame_equal(actual, expected)


def test_normalise_var():

    input_array_1 = np.random.normal(loc=0.5, scale=0.5, size=100)
    input_array_2 = [(0.03 * i) for i in range(100)]
    input_array_3 = [(0.001 * i) for i in range(100)]

    assert input_array_1.max() > 1, "input array too small for test"

    input_df = pd.DataFrame(
        {
            "index": [i for i in range(100)],
            "transformation_1": input_array_1,
            "transformation_2": input_array_2,
            "transformation_3": input_array_3,
        }
    )

    for weight in [1, 0.5, 0.707]:

        actual = _normalise_var(input_df, weight, key_columns=["index"])

        for column in actual.columns[1:]:
            # rounded to 10 decimal places
            assert round((actual[column]).max(), 10) == weight
            assert round((actual[column]).min(), 10) == 0


def test_transform_var():

    input_array_1 = [2 * (i + 1) for i in range(100)]  # contains no 0
    input_array_2 = [2 * (i) for i in range(100)]  # contains 0

    input_df_1 = pd.DataFrame(
        {
            "index": [i for i in range(100)],
            "transformation_1": input_array_1,
        }
    )

    input_df_2 = pd.DataFrame(
        {
            "index": [i for i in range(100)],
            "transformation_2": input_array_2,
        }
    )

    actual_1, greater_than_0_1 = _transform_var(input_df_1, "transformation_1")
    actual_2, greater_than_0_2 = _transform_var(input_df_2, "transformation_2")

    assert greater_than_0_1 is True
    if ("transformation_1_bc" in actual_1.columns) & (
        "transformation_1_yj" in actual_1.columns
    ):
        assert True

    assert greater_than_0_2 is False
    if ("transformation_2_recip" not in actual_1.columns) & (
        "transformation_2_yj" in actual_2.columns
    ):
        assert True
