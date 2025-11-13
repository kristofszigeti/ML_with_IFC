from pathlib import Path
import pandas

# INPUT
input_path = Path("../data/output/TC_OF3.csv")

# LOGIC
dataframe = pandas.read_csv(input_path)
mapping = {"--":0} # kikeresi a megadott string-et és helyettesíti mással. itt számszerű, bináris értéket akarok elérni
dataframe_cleaned = dataframe.replace(mapping)

# OUTPUT
output_path = Path("../data/output/TC_OF3_clean.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

dataframe_cleaned.to_csv(output_path, index=False)
print(dataframe_cleaned.head())