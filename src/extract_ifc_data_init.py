# =============================================
# extract_ifc_data.py
# =============================================
# 7.4.2. Data Extraction from IFC
import ifcopenshell # loads package for handling ifc files
import pandas # loads package for handling data
from pathlib import Path # imports the Path class, which is used to manipulate file paths
"""
This script is used to extract data from the IFC file.
To achieve this, it opens the file, parses it, and extracts the data.
For opening the file, it uses the 'ifcopenshell' package.
For parsing the file, it uses the 'ifcopenshell.util.element' module.
During the parsing step, it checks if the element is a beam, and if it is, with the library pandas, it extracts the GUID, Name, and Type. 
An initial empty list is created to store the extracted data. For-loop is used to iterate over the beams.
For extracting the data, it uses the 'pandas' package.
At the end, it saves the extracted data to a beam_data.csv file.
"""
print("*** This is the start. *** \n")
# INPUT
# Open the IFC file, 'r' for reading
ifc_path = Path("../data/input/OF3.ifc") # path to the IFC file within the project folder

try:
    ifc_model = ifcopenshell.open(ifc_path) # opens the file path and only opens the file path, does not parse it yet
    print(f"IFC file path: {ifc_path}. \nPath is okay, the file is opened.")
except Exception as e:
    print(f"Error while opening the IFC file. {e} Check the file path.")

out_path = Path("../data/output/beam_data.csv") # this is the output path for the csv file
# stores the beams from the IFC model in a variable
# ifc_beam_byname = ifc_model.by_name("BEAM") # AttributeError: nincs 'by_name'
ifc_beams = ifc_model.by_type("IfcBeam") # minden "IfcBeam"; tudjuk, hogy van ifcBeam => kell, hogy találjon
number_of_beams = len(ifc_beams)
if ifc_beams is None: # if there is no 'IfcBeam' in the ifc model.
    raise Exception("IFC file does not contain any beams.")
else:
    print(f"IFC file contains {number_of_beams} pieces of ifcBeam.")

# INIT: csak egy üres lista, amihez hozzáfűzzük a kinyert ifc_beam-eket
beam_data = []

for ifc_beam in ifc_beams:
    beam_guid = ifc_beam.GlobalId # GUID, # ez az az egyértelmű azonosító, amit a natív modellből kap az objektum, amikor létrehozzuk
    beam_name = ifc_beam.Name # Name, user provided name
    element_type = ifc_beam.is_a() # visszaadja az ifc osztály típusát, amit lekérdeztünk 21. sorban
    # element_check = None
    if element_type == "IfcBeam" and beam_name == "BEAM":
        element_check = "OK"
    else:
        element_check = "Anomaly?"
    # append the variables to the previously initialized empty list
    beam_data.append([beam_guid, beam_name, element_type])

# now, i'm having data extracted from ifc model
# Next step is creating a csv for ML model
# spreadsheet as pandas dataframe for furtherer operations
beam_dataframe = pandas.DataFrame(beam_data, columns=["GUID", "Name", "Type"])
# ellenőrzés a terminálon:
# print(beam_dataframe) # displays the whole dataframe
print(beam_dataframe.head(10)) # quick preview, displays only 10 rows if the dataframe
csv_dataset = beam_dataframe.to_csv(r"..\data\output\beam_data.csv", index=False) # wo row index
# az 'r' segít meggátolni a speciális string karakterkombók kezelését
# print(csv_dataset) # -> None
print("\n *** This is the end. ***")
# =============================================
#   END OF THIS SCRIPT
# =============================================