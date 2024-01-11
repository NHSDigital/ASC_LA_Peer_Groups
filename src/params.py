"""
Pathway Parameters
"""
data_folder = "data"
output_folder = "output"
raw_folder = "raw"
interim_folder = "interim"
primary_folder = "primary"
processed_folder = "processed"
report_folder = "reports"
transformations_folder = "transformations"
pipeline_runs = "pipeline_runs"

LSOA_code = "LSOA21CD"
LSOA2011_code = "LSOA11CD"

"""
Data File Names
"""
LSOA_UTLA_lookup_file = "LSOA21_to_UTLA22.csv"
area_file = "area_sqkm.csv"
ethnicity_data_file = "ethnicity.csv"
retail_floorspace_data_file = "retail_floorspace.csv"
nssec_data_file = "ns-sec.csv"
council_bands_data_file = "council_tax_bands.csv"
rateable_value_data_file = "rateable_value.csv"
population_data_file = "population_data.csv"
coastal_file = "coastal.csv"
english_proficiency_data_file = "english_proficiency.csv"
housing_tenure_data_file = "housing_tenure.csv"
qualification_level_data_file = "qualification_level.csv"
rooms_file = "rooms.csv"
distance_to_sea_file = "distance_to_sea.csv"
sparsity_file = "sparsity.csv"
aggregated_file = "aggregated.csv"

"""
Report and Output Values
"""

high_corr_value = 0.8

"""
Columns
"""
example_utlas = [
    "Cheshire West and Chester",
    "Harrow",
    "Herefordshire",
    "Lambeth",
    "Norfolk",
    "North East Lincolnshire",
    "Plymouth",
    "Reading",
    "South Tyneside",
    "Leeds",
]

pop_geo_code = "geography code"
pop_geo_col = "geography"
over_18_population = "Over 18 Population"
over_15_population = "Over 15 Population"
age_65_to_84_population = "Aged 65 to 84 Population"
over_85_population = "85 and over Population"
over_85_population_original_name = "Age: Aged 85 years and over"
total_population = "Age: Total"

retail_floorspace = "retail_floorspace"
rateable_value = "non_domestic_rateable_value"

pop_columns_to_add = [
    "Age: Aged 15 to 19 years",
    "Age: Aged 20 to 24 years",
    "Age: Aged 25 to 29 years",
    "Age: Aged 30 to 34 years",
    "Age: Aged 35 to 39 years",
    "Age: Aged 40 to 44 years",
    "Age: Aged 45 to 49 years",
    "Age: Aged 50 to 54 years",
    "Age: Aged 55 to 59 years",
    "Age: Aged 60 to 64 years",
    "Age: Aged 65 to 69 years",
    "Age: Aged 70 to 74 years",
    "Age: Aged 75 to 79 years",
    "Age: Aged 80 to 84 years",
    "Age: Aged 85 years and over",
]

# density
area_sq_km = "Extent of the Realm (Area in KM2)"
pop_density_column = "People per square km"
pop_density_lsoa_column = "People per square km (LSOA)"

# ethnicity
ethnicity_geo_col = "geography code"
ethnic_group_cols_to_keep = {
    "LSOA21CD": "geography code",
    "total": "Ethnic group: Total: All usual residents",
    "black african": "Ethnic group: Black, Black British, Black Welsh, Caribbean or African: African",
    "black caribbean": "Ethnic group: Black, Black British, Black Welsh, Caribbean or African: Caribbean",
    "bangladeshi": "Ethnic group: Asian, Asian British or Asian Welsh: Bangladeshi",
    "chinese": "Ethnic group: Asian, Asian British or Asian Welsh: Chinese",
    "indian": "Ethnic group: Asian, Asian British or Asian Welsh: Indian",
    "pakistani": "Ethnic group: Asian, Asian British or Asian Welsh: Pakistani",
    "mixed": "Ethnic group: Mixed or Multiple ethnic groups",
    "white": "Ethnic group: White",
}

# NS-SEC
nssec_total = "National Statistics Socio-economic Classification (NS-SEC): Total: All usual residents aged 16 years and over"
nssec_routine_manual_occupations = [
    "National Statistics Socio-economic Classification (NS-SEC): L10 and L11 Lower supervisory and technical occupations",
    "National Statistics Socio-economic Classification (NS-SEC): L12 Semi-routine occupations",
    "National Statistics Socio-economic Classification (NS-SEC): L13 Routine occupations",
]
nssec_student = (
    "National Statistics Socio-economic Classification (NS-SEC): L15 Full-time students"
)
processed_nssec_total = "total"
processed_nssec_student = "student"
processed_routine_manual = "routine_manual"

# Council tax
council_tax_geocode = "ecode"
council_tax_total = "total_properties"
council_tax_lower = "lower_council_tax_bands"
council_tax_lower_bands = "abcd"
# English proficiency
eng_prof_total = (
    "Proficiency in English language: Total: All usual residents aged 3 years and over"
)
eng_prof_low = [
    "Proficiency in English language: Main language is not English (English or Welsh in Wales): Cannot speak English well",
    "Proficiency in English language: Main language is not English (English or Welsh in Wales): Cannot speak English",
]
processed_eng_prof_low = "low_english_proficiency"
processed_eng_prof_total = "total"

# Housing tenure
housing_tenure_total = "Tenure of household: Total: All households"
housing_tenure_ownership = "Tenure of household: Owned"
housing_tenure_social_rent = "Tenure of household: Social rented"
processed_tenure_total = "total"
processed_owners = "home_owners"
processed_renters = "social_renters"


# Qualification level
qual_level_total = (
    "Highest level of qualification: Total: All usual residents aged 16 years and over"
)
higher_qual_level = "Highest level of qualification: Level 4 qualifications and above"
processed_qual_level_higher = "higher_level_qualifications"
processed_qual_level_total = "total"

# Rooms
rooms_col_prefix = "Number of rooms (VOA): "
rooms_total = "Total: All households"
room_limit = 4
few_rooms = "few_rooms"
rooms_total_col = "total"

# Distance to sea
distance_to_sea = "Distance to Sea (km)"

# Sparsity
sparsity = "Sparsity (% population living in low density areas)"
