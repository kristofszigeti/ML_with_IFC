import pandas
from pathlib import Path

# visszakötés GUID
input_path = Path("../data/output/beam_data.csv")
output_path= Path("../data/output/features_w_guid.csv")

# beolvassuk
dataframe = pandas.read_csv(input_path)

