"""
Feldolgozza a csv-t és az értéknélküli mezőket 0-val helyettesíti
"""

from pathlib import Path
import pandas

# INPUT
input_path = Path("../../data/output/csv_dataframe/OF3_parts_Pset01_dataframe.csv")

# LOGIC
dataframe = pandas.read_csv(input_path)
mapping = {"--":0} # kikeresi a megadott string-et és helyettesíti mással. itt számszerű, bináris értéket akarok elérni
dataframe_cleaned = dataframe.replace(mapping)

# OUTPUT
output_path = Path("../../data/output/csv_dataframe/OF3_parts_Pset01_dataframe.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

dataframe_cleaned.to_csv(output_path, index=False)
print(dataframe_cleaned.head())