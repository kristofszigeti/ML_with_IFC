
# 7.4.3. Data preprocessing
import pandas
from pathlib import Path
""" 
This script is used to preprocess the data.
Adds a new column with only ones, and saves it to a csv file.
It is going to be called 'features_dummy.csv'.
Provides numerical data for the ML model, 
but narrowed down to only numerical values to set up the data pipeline.
"""


# declaring INPUT csv and OUTPUT csv
input_path = Path("../data/output/csv_dataframe/plate_features.csv")

# assigning the input csv path to a variable
dataframe = pandas.read_csv(input_path)
# print(dataframe) # original dataframe

# creating a new column as temporary storage for numerical values inside the dataframe with only ones.
dataframe_boltcount = dataframe[["Bolt Count"]]
# print(dataframe) # original + Column "Feature" with 1-s created

# 6) Rövid riport kiírása ellenőrzésképpen
print("Eredeti sorok száma   :", len(dataframe_boltcount))
print("Felhasználható sorok  :", len(dataframe_boltcount))
print("bolt_count statisztika:")
print(dataframe_boltcount["Bolt Count"].describe())   # Min, max, átlag stb.

output_path = Path("../data/output/features.csv") # output path of 'features_dummy.csv'
output_path.parent.mkdir(parents=True, exist_ok=True) # a mapparendszer és útvonal biztosítása, készítése és hibakezelés/elkerülés
# parents means parent directories, exist_ok means don't throw an error if the directory already exists'

# saving the numerical data frame to a csv file
dataframe_boltcount.to_csv(output_path, index=False) # outputs the numerical data frame to the 'features_dummy.csv' file in !only one! column
# print(output_numerical_data_frame.head()) # checking the output

print("Done. features.csv:")

print(f"Bolt Count features dataframe saved to: {output_path}")
print(dataframe_boltcount.head())