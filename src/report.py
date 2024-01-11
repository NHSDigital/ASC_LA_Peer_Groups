from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.colors as plt_colours
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import src.params as params

INPUT_PATH = Path(params.data_folder).joinpath(params.primary_folder)


def create_histogram(
    output: str,
    df: pd.DataFrame,
    col: str,
    fig_name: str,
    bins: int = 10,
    y_title: str = "UTLA Count",
) -> None:
    """
    Creates a histogram for a given feature.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing aggregated UTLA data.
    col : str
        Name of column to create histogram with.
    fig_name : str
        Name to save the figure. Should end with .png.
    bins : int, optional
        Number of bins the histogram is split by.
        The default is 10.
    y_title : str, optional
        The label on the y axis.
        The default is "UTLA Count".

    Outputs
    -------
    Saves a histogram for the set column in the report.

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots(figsize=(8, 6))
    df.hist(column=col, bins=bins, ax=ax)
    ax.set_xlabel(col)
    ax.set_ylabel(y_title)
    for path in [params.report_folder, output]:
        fig.savefig(Path(path).joinpath(fig_name))

    plt.close()

    return None


def create_corrplot(
    output: str,
    df: pd.DataFrame,
    cmap: str = "Blues",
    symmetrical: bool = True,
):
    """
       Creates a correlation matrix plot for all features.

       Parameters
       ----------
       df : pd.DataFrame
           Dataframe containing all aggregated UTLA data.
       cmap : str, optional
           The python colour map used to colour the correlation plot.
           The default is "Blues".
       symmetrical : bool, optional
           If true, uses a symmetric colour map to show more clearly the absolute
           correlation between features.
           The default is True.
    -m "
       Outputs
       -------
       Saves a coloured correlation plot in report.

       Returns
       -------
       corr
           Correlation Matrix.

    """

    if symmetrical:
        cmap_settings = (
            cmap,
            None,
        )
        mymap = symmetrical_colormap(cmap_settings=cmap_settings, new_name=None)
    else:
        mymap = cmap

    f = plt.figure(figsize=(19, 15))
    corr = df.corr()
    plt.matshow(corr, fignum=f.number, cmap=mymap, vmin=-1, vmax=1)
    plt.xticks(
        range(df.select_dtypes(["number"]).shape[1]),
        df.columns,
        fontsize=14,
        rotation=90,
    )
    plt.yticks(
        range(df.select_dtypes(["number"]).shape[1]),
        df.columns,
        fontsize=14,
    )
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=14)
    plt.title("Correlation Matrix", fontsize=16)

    title_string = "corr_matrix_plot"
    if symmetrical:
        title_string += "_sym"

    for path in [Path(params.report_folder), output]:
        plt.savefig(Path(path).joinpath(title_string))

    plt.close()

    return corr


def symmetrical_colormap(
    cmap_settings: Tuple[str, Optional[int]], new_name: Optional[str]
):
    """
    Generates a symmetrical colour map.

    Parameters
    ----------
    cmap_settings : (str, int or None)
        First string is the python colour map which will be made symmetrical.
        Int or None represents the lut. If the name is not already a Colormap
        instance and lut is not None, the colormap will be resampled to have
        lut entries in the lookup table.
    new_name : None or Str, optional
        The name of the newly generated colour map. The default is None.

    Returns
    -------
    symmetrical_colour_map
        Symmetrical colour map.

    """
    cmap = plt.get_cmap(*cmap_settings)
    if not new_name:
        new_name = "sym_" + cmap_settings[0]  # ex: 'sym_Blues'

    n = 128
    colours_r = cmap(np.linspace(0, 1, n))
    colours_l = colours_r[::-1]
    colours = np.vstack((colours_l, colours_r))
    symmetrical_colour_map = plt_colours.LinearSegmentedColormap.from_list(
        new_name, colours
    )

    return symmetrical_colour_map


def show_high_correlation(
    output: str,
    df: pd.DataFrame,
    corr: pd.DataFrame,
    high_value: float = params.high_corr_value,
) -> None:
    """
    Checks feature pairs with a high correlation.
    Outputs scatter graphs of these feature pairs so they can be examined.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing all aggregated UTLA data.
    corr : pd.DataFrame
        Dataframe in form of a correlation matrix between all features.
    high_value : float, optional
        Pearson coefficient value, correlations with a value greater than this will
        be plotted separately in the report and logged.
        The default is params.high_corr_value.

    Outputs
    -------
    Outputs scatter plots between feature pairs with a Pearson Coefficient  greater
    than high_value.

    Returns
    -------
    None.

    """
    print(type(corr))
    corr = corr.abs().stack().reset_index()
    corr.columns = ["Var 1", "Var 2", "Corr"]
    mask_dupes = (corr[["Var 1", "Var 2"]].apply(frozenset, axis=1).duplicated()) | (
        corr["Var 1"] == corr["Var 2"]
    )
    corr = corr[~mask_dupes]

    high_corr = corr[corr["Corr"] > high_value].sort_values("Corr", ascending=False)
    print(f"feature pairs greater than {high_value}:")
    print(high_corr)
    print("Creating scatter plots for these feature pairs.")

    n_vars = corr["Var 1"].nunique()
    avg_corr = corr["Corr"].sum() / corr.shape[0]
    print(f"Average Pearson correlation coefficient per feature pair: {avg_corr}")
    corr_by_val = (corr.groupby("Var 1")["Corr"].sum() / (n_vars - 1)).sort_values(
        ascending=False
    )
    print("Average Pearson correlation across all pairs:")
    print(corr_by_val)

    for index, row in high_corr.iterrows():
        x_values = df[row["Var 1"]]
        y_values = df[row["Var 2"]]

        all_data = pd.merge(x_values, y_values, left_index=True, right_index=True)

        fig, ax = plt.subplots(figsize=(8, 6))
        all_data.plot.scatter(x=row["Var 1"], y=row["Var 2"], ax=ax)
        plt.title(f"Pearson Correlation: {round(row['Corr'],3)}")

        for path in [Path(params.report_folder), output]:
            fig.savefig(Path(path).joinpath(f"{row['Var 1']}_{row['Var 2']}_Corr"))

        plt.close()
    print(f"Scatter plots stored in {params.report_folder}")

    return None


def run_report(la_code: str, output_folders: List[str], features: List[str]) -> None:

    """
    Runs the report, which outputs multiple graphs for examination by the user.
    Calls other functions within this file.

    Parameters
    ----------

    output_folders: list,
        List containing 4 separate paths to the specified output folder.
    features : List[str]
        A list containing all the features to be used in the Euclidean distance
        and report calculation.
    la_code: str
        The UTLA code to be used. e.g."UTLA22CD".

    Returns
    -------
    None.
    """
    OUT_REPORTS = output_folders[2]

    print("Creating histograms for each feature distribution across UTLAs")

    # create a list of features with weights greater than 0
    features = [k for k in features.keys() if features[k] > 0]

    df = pd.read_csv(
        Path(INPUT_PATH).joinpath(params.aggregated_file),
        index_col=la_code,
        usecols=[la_code] + features,
    )
    for feature in features:
        create_histogram(
            df=df,
            col=feature,
            fig_name=f"{feature}_histogram.png",
            bins=25,
            output=OUT_REPORTS,
        )
    print(f"All histograms created, saved at: {params.report_folder}")

    print("Creating correlation matrices showing correlation between each feature")
    create_corrplot(OUT_REPORTS, df, symmetrical=True, cmap="Blues")
    correlations = create_corrplot(OUT_REPORTS, df, symmetrical=False, cmap="coolwarm")
    print(f"All correlation matrices created, saved at: {params.report_folder}")

    show_high_correlation(
        output=OUT_REPORTS,
        df=df,
        corr=correlations,
        high_value=params.high_corr_value,
    )
    print("High correlations may affect outputs.")
    print("You may wish to consider not including features in analysis, see config")
    print("Transforming and Plotting features")
    print("Report Complete")

    return None


def transformation_report(
    output: str,
    df: pd.DataFrame,
    feature: str,
    normalise: bool,
    greater_than_zero: bool,
) -> None:
    """
    Produces a report of histograms of datasets with multiple transformations applied.

    Parameters
    ----------
    output : str,
        A path to a specified output folder.
    df :  pd.DataFrame
        Dataframe containing aggregated UTLA data.
    feature : str
        feature / Column Name to be transformed.
    normalise : bool
        If true, all values will be between 0 and 1.
    greater_than_zero : bool
        Set as true if the data contains only greater than 0 values.
        This will ensure transformations that cannot handle 0 values will not run.


    Outputs
    -------
    Graph containing histograms for each transformation for given feature.

    Returns
    -------
    None.
    """

    rows, cols = 2, 4
    fig, ax = plt.subplots(rows, cols, sharex="col", sharey="row", figsize=(18, 8))

    ax[0, 0].hist(df[feature], bins=25)
    ax[0, 0].set_title("No transformation")
    ax[0, 1].hist(df[f"{feature}_sqrr"], bins=25)
    ax[0, 1].set_title("Square Root")
    ax[0, 2].hist(df[f"{feature}_yj"], bins=25)
    ax[0, 2].set_title("Yeo Johnson")
    ax[0, 3].hist(df[f"{feature}_log"], bins=25)
    ax[0, 3].set_title("Simple Log")
    ax[1, 1].hist(df[f"{feature}_squared"], bins=25)
    ax[1, 1].set_title("Squared")

    if greater_than_zero > 0:
        ax[1, 0].hist(df[f"{feature}_recip_sqrr"], bins=25)
        ax[1, 3].hist(df[f"{feature}_bc"], bins=25)
        ax[1, 2].hist(df[f"{feature}_recip"], bins=25)
    else:
        ax[1, 3].text(0.5, 0.5, "Not Possible\ndata contains 0 values", ha="center")
        ax[1, 0].text(0.5, 0.5, "Not Possible\ndata contains 0 values", ha="center")
        ax[1, 2].text(0.5, 0.5, "Not Possible\ndata contains 0 values", ha="center")
    ax[1, 3].set_title("Box Cox")
    ax[1, 0].set_title("Reciprocal Square Root")
    ax[1, 2].set_title("Reciprocal")

    fig.suptitle(f"feature: {feature}, Normalised: {normalise}")

    for path in [
        Path(params.report_folder).joinpath(params.transformations_folder),
        output,
    ]:
        fig.savefig(Path(path).joinpath(f"{feature}"))

    plt.close()

    return None
