
# 7.4.3. Data preprocessing
import pandas
from pathlib import Path
""" 
This script is used to preprocess the data.
Adds a new column with only ones, and saves it to a csv file.
It is going to be called 'features.csv'.
Provides numerical data for the ML model, 
but narrowed down to only numerical values to set up the data pipeline.
"""


# declaring INPUT csv and OUTPUT csv
input_path = Path("../data/output/beam_data.csv")

output_path = Path("../data/output/features.csv") # output path of 'features.csv'
output_path.parent.mkdir(parents=True, exist_ok=True) # a mapparendszer és útvonal biztosítása, készítése és hibakezelés/elkerülés
# parents means parent directories, exist_ok means don't throw an error if the directory already exists'

# assigning the input csv path to a variable
input_data_frame = pandas.read_csv(input_path)
# print(input_data_frame) # original dataframe

# creating a new column as temporary storage for numerical values inside the dataframe with only ones.
input_data_frame["Feature"] = 1
# print(input_data_frame) # original + Column "Feature" with 1-s created

# keeping only this numerical Feature column
output_numerical_data_frame = input_data_frame[["Feature"]]
print(output_numerical_data_frame) # csak az 1-esek

# saving the numerical data frame to a csv file
output_numerical_data_frame.to_csv(output_path, index=False) # outputs the numerical data frame to the 'features.csv' file in !only one! column
print(output_numerical_data_frame.head()) # checking the output