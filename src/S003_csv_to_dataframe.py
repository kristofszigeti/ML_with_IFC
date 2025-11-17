

import pandas
from pathlib import Path

# now, i'm having data extracted from ifc model
# simple comma separated values (csv) file, NO dataframe
input_csv_filename = "OF3_parts_Pset01"

# INPUT
input_path = Path(f"../data/input/csv/{input_csv_filename}.csv")

# LOGIC
# spreadsheet as pandas dataframe for furtherer operations
# Next step is creating a csv dataframe for ML model
dataframe = pandas.read_csv(input_path) # it is a dataframe from now on
# how to get rid of certain columns
dataframe = dataframe.drop(columns=["GUID", "Product Name", "Product Description"])

# ellenőrzés a terminálon:
# print(dataframe) # displays the whole dataframe
print(dataframe.head(10)) # quick preview, displays only 10 rows if the dataframe

output_path = Path(f"../data/output/csv_dataframe/{input_csv_filename}_dataframe.csv")
output_csv_filename = f"{input_csv_filename}_dataframe"
output_path.parent.mkdir(parents=True, exist_ok=True)
csv_dataset = dataframe.to_csv(output_path, index=False) # wo row index
# az 'r' segít meggátolni a speciális string karakterkombók kezelését ## helyette: pathlib -> Path funkció
# print(csv_dataset) # -> None


print("\n The dataframe is ready for ML."
      "\n *** This is the end. ***")
# =============================================
#   END OF THIS SCRIPT
# =============================================