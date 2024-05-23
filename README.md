# Peer Groups for Local Authorities

Calculates statistical neighbours (aka peers) for Local Authorities in England, for use in Adult Social Care statistics.

## Contact

This repository is maintained by the NHS England Adult Social Care Statistics Team.

> To contact us raise an issue on Github or via email at [socialcare.statistics@nhs.net](mailto:socialcare.statistics@nhs.net).
> See our (and our colleagues') other work here: [NHS England Analytical Services](https://github.com/NHSDigital/data-analytics-services).

## Description

This repository was developed by the Data Science team for the Adult Social Care Statistics team, to provide a way of comparing statistics between 'similar' Local Authorities.

We have calculated a metric of similarity (Euclidean distance) based on standardised, normalised input features from Census 2021 data, including population demographics such as age, ethnicity and educational attainment.

## Setup

* This project was developed using Python 3.10.5
* Required Python libraries are listed in `requirements.txt`
* _Optional:_: Python libraries used for linting are included in `dev-requirements.txt`. See the [developing the pipeline](#developing-the-pipeline) section for more details about linting configuration.

### Set up a virtual environment

Clone this project and ensure you're in the root directory, ASC_LA_Peer_Groups. You can change your current directory in the terminal e.g.

```bash
cd ASC_LA_Peer_Groups
```

Set up a virtual environment and install requirements:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

```

## Getting started

### Configuring the pipeline

The configuration for the pipeline is defined in `config.toml`. If you want to adjust the weights of any of the inputs features (including adding or removing features), change the UTLA definitions etc., make the required edits in the `config.toml`.

There are four sections:

1. `[LOCATION]` - locations used by the pipeline. This includes where the input data is stored, as well as where logs and outputs are saved. The location of your input and output directories need setting up in the `config.toml`.
    
    <details>
            <summary>Notes on file path</summary>

 

    * Data files should be downloaded and stored to the location specified in `config.toml`. This must be outside of this repository, and can be a shared drive location
    * Also note that file paths should contain **forward** slashes e.g. "C:/Users/username/Documents/data"


    </details>
2. `[LOCAL_AUTHORITY]` - defines the local authority codes to use
3. `[MODEL_OUTPUT]` - defines changeable characteristics of the output. Currently this only includes `n_peers` which limits the number of closest nearest neighbours output by the model.

    <details>
        <summary>Model output defaults</summary>

    ```toml
    n_peers = 15
    ```

    </details>

4. `[FEATURE_WEIGHTS]` - lists features along with their associated weights. Note that a weight of zero reduces the effect of the feature to zero and thereby excludes it completely.

    <details>
        <summary>Feature weight defaults</summary>

    ```toml
    "Over 15 Population" = 1
    "85 and over Population %" = 1
    "Aged 65 to 84 Population %" = 0
    "black african %" = 0.5
    "black caribbean %" = 0.5
    "bangladeshi %" = 0.5
    "indian %" = 0.5
    "chinese %" = 0.5
    "pakistani %" = 0.5
    "mixed %" = 0
    "white %" = 0
    "home_owners %" = 0
    "social_renters %" = 1
    "student %" = 1
    "routine_manual %" = 0
    "low_english_proficiency %" = 1
    "People per square km" = 1
    "higher_level_qualifications %" = 1
    "few_rooms %" = 0
    "Distance to Sea (km)" = 0.5
    "Sparsity (% population living in low density areas)" = 1
    ```

    </details>

5. `[REMOVE_LAS]` - lists UTLAs to be excluded from analysis. For example ["Isles of Scilly", "City of London"]. Please use the name of the Local Authority, using the `la_name` field defined in `[LOCAL_AUTHORITY]` above.
    <details>
        <summary>Default removed UTLAs</summary>NHS England remove Isle of Scilly and City of London from the default model. I.e.:

    ```toml
    las_to_remove = ["Isles of Scilly", "City of London"]
    ```

    </details>

### Data

Data files should be downloaded and stored to the location specified in `config.toml`. This must be outside of this repository, and can be a shared drive location.

1. Download ten CSV files and save them to the input location specified in the `config.toml`. The names of the files and their sources are provided below. Some files are only available as part of a collection, in which case the source is listed as a zip file containing more than one csv. Where this is the case, download and extract the zip file saving the file version which ends 'lsoa'.


| Save as file name | Source | Details |
| ----------------- | ------ | ------- |
| area_sqkm.csv | https://geoportal.statistics.gov.uk/datasets/a488cb8fc9a74accb63cb52961e456ef/about | Click the Download button at the top of the page. Within the subfolder "Measurements", rename the file "SAM_LSOA_DEC_2021_EW_in_KM" to "area_sqkm.csv" | 
| distance_to_sea.csv | https://digital.nhs.uk/supplementary-information/2024/distance-to-sea-calculations | Download the csv data file and rename to distance_to_sea.csv |
| english_proficiency.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts029.zip | Download the zip folder. Rename the csv ending in "lsoa" to "english_proficiency" |
| ethnicity.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts021.zip | Download the zip folder. Rename the csv ending in "lsoa" to "ethnicity" |
| housing_tenure.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts054.zip | Download the zip folder. Rename the csv ending in "lsoa" to "housing_tenure" |
| ns-sec.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts062.zip | Download the zip folder. Rename the csv ending in "lsoa" to "ns-sec" |
| population_data.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts007a.zip | Download the zip folder. Rename the csv ending in "lsoa" to "population_data" |
| qualification_level.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts067.zip | Download the zip folder. Rename the csv ending in "lsoa" to "qualification_level" |
| rooms.csv | https://www.nomisweb.co.uk/output/census/2021/census2021-ts051.zip | Download the zip folder. Rename the csv ending in "lsoa" to "rooms" |
| LSOA21_to_UTLA22.csv | https://geoportal.statistics.gov.uk/datasets/ons::lower-layer-super-output-area-2021-to-upper-tier-local-authorities-2022-lookup-in-england-and-wales-v2/explore | Click the download button, select the CSV download option. Rename this file to LSOA21_to_UTLA22 |

**A note on lookups:** The final CSV file listed above, `LSOA21_to_UTLA22.csv` , maps LSOAs to UTLAs (local authorities).
    
    E.g.:

    | LSOA21_CODE | LSOA21_NAME       | UTLA_CODE | UTLA_NAME     |
    |-------------|-------------------|-----------|---------------|
    | E01012052   |Middlesbrough 014D | E06000002 | Middlesbrough |

    | Save as file name | Source |
    | ----------------- | ------ |


### Running the pipeline

> **NOTE:** Please edit the `LOCATION` in `config.py` before running the pipeline.

Once you've initially setup the virtual environment in the previous steps, ensure you're in the virtual environment by running the code `.venv\Scripts\activate` in the terminal.

Once you've activated your virtual environment, run the following code from the terminal:

```bash
python main.py
```

If you want to adjust the weights of any of the inputs features (including adding or removing features), change the UTLA definitions etc., make the required edits in the `config.toml`.

_(Optional)_ Adding a custom hash:

To make your pipeline run easier to identify, it is possible to pass a custom hash to name your pipeline. This means log names and your output pipeline folder name will include the hash.

The hash length is set in `config.toml`- if you supply a shorter hash this is fine, but be aware that a longer hash will be cropped to the first n characters using the hash length.

```bash
python main.py --hash my_run
```

Where `my_run` is the custom hash you have supplied.

### Outputs

This pipeline produces the following as _final_ outputs, saved to the `outputs` directory:

* `features.csv` - The final features used to produce the distances
* `distances.csv` - Distance between each pair of local authorities
* `peers.csv` - N most similar peers for each local authority (n defined in `config.toml`)
* `example_peers.csv` - The above but limited to a subset of local authorities specified in `src/params.py`

Reports to accompany these outputs, including details of correlation between features and feature distributions, are saved to the `reports` directory.

Final outputs and reports are saved to a pipeline folder saved in the output directory defined in `config.toml`. The name of each pipeline folder corresponds to the time the pipeline was initialised, and any custom hash that was provided.

Interim data processing produces files saved to the `data/` directory- these are NOT copied to the pipeline output location.

## Updating and adding new data

### Updating the lookup file

To change your LSOA to UTLA lookup, copy across the new lookup to the location in `config.toml`, ensuring to give it a unique name ending with ".csv". Ensure the new lookup has no blank space above the headers, and make a note of the header names.

Navigate to `src\params.py`, go to the "Lookup Pathways and Parameters" section and change the name of the `LSOA_UTLA_lookup_file` to the new lookup. If the LSOA code column name in the new lookup has changed, you will also need to update `LSOA_code` to the corresponding column name.

If you have updated `LSOA_code`, you will need to check the rest of `src\params` for references to the old LSOA code. For example, in the ethnicity section of `params.py`.

Navigate to `config.toml` and ensure the `la_code` and `la_name` match the names of the relevant columns in your new lookup.

You can now run the pipeline with the updated lookup.

### Adding New Data

New data and lookups can be added easily to the pipeline. All new data and lookups should be stored in the input directory, as specified in the config file as ‘input_dir’. Data files should all be in a data\input\raw folder from the input directory and look up files should all be in a `data\lookups\raw` folder from the input directory.

To add new data to the pipeline, navigate to the `data\input\raw` folder within the input storage. replacing an existing csv file, ensure to either archive/delete the old file, or rename the new file with a unique name. The new file should be checked to ensure it is in the same format as the old file.

In `src/params.py`, check the “Data File Names” section, and ensure the name of the replaced file matches the corresponding file name in the params.  Further to this, check the column values in the “Columns” section of params for the feature you have changed, and ensure these match the columns within the new data.

### Boundary changes

The following steps will be needed to update the code to include the latest council borders:

1. Download the latest LSOA data, the links are provided above.
2. Check all column names match, if using the April 23 ons file, 'UTLA23NM' will need to be renamed to 'UTLA22NM'.
3. Replace the files 'LSOA_AREA_KM' and 'LSOA21_to_UTLA22' in the lookup folder.

The code will now use the new boundary definitions when calculating the Euclidean Distances for each of the variables.

## Project structure

```text
| .gitignore                <- ignores data and virtual environment files
| .pre-commit-config.yaml   <- configuration for pre-commit hooks (optional, see above)
| config.toml               <- options for modelling, e.g. output location, k etc.
| requirements.txt          <- python libraries required
| dev_requirements.txt      <- python libraries required for development (optional, includes linting libraries)
| LICENSE                   <- license info for public distribution
|
+---reports                 <- This is a placeholder which the pipeline populates with report outputs (e.g. histograms showing feature distributions)
|
+---outputs                 <- This is a placeholder which the pipeline populates with output data
|
| main.py                   <- Runs the pipeline
|
+---data                    <- This is a placeholder which the pipeline populates with data
|   +---raw
|   +---interim
|   +---primary
|
+--- src                    <- Scripts with functions used in main.py
|   |   __init__.py         <- Makes the scripts importable python modules
|   |   params.py           <- configures column names, file paths etc.
|   |   load.py             <- Copies input files from location specified in config
|   |   clean.py            <- Cleans input data to LSOA level
|   |   process.py          <- Aggregates cleaned data to UTLA level
|   |   model.py            <- Calculates distance metric
|   |   report.py           <- Produces accompanying reports e.g. correlation
|   |   utils.py            <- Useful functions used across modules
|
```

## Developing the pipeline

_(Optional)_ Install dev requirements and setup pre-commit hooks:


```bash
pip install -r dev_requirements.txt
pre-commit install
```

You can also run the testing suite once these requirements have been installed:

```bash
pytest
```

## Contributors

This codebase was originally developed by [Harriet Sands](https://github.com/harrietrs) and [Will Poulett](https://github.com/willpoulett), with help from the Adult Social Care Team at NHS England.

## Licence

This codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government 3.0 licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
