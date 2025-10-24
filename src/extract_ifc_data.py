import ifcopenshell # loads package for handling ifc files
import pandas # loads package for handling data

# 7.4.2. Data Extraction
# Open the IFC file, 'r' for reading
ifc_path = r"..\data\input\OF3.ifc" # path to the IFC file within the project folder
ifc_model = ifcopenshell.open(ifc_path) # opens the file path and only opens the file path, does not parse it yet

# stores the beams from the IFC model in a variable
# ifc_beamsbyname = ifc_model.by_name("BEAM") # AttributeError: nincs ilyen attribútuma a
ifc_beams = ifc_model.by_type("IfcBeam") # minden "IfcBeam"; tudjuk, hogy van ifcBeam => kell, hogy találjon
# ez az az egyértelmű azonosító, amit a natív modellből kap az objektum, amikor létrehozzuk

# csak egy üres lista, amihez hozzáfűzzük a kinyert ifc_beam-eket
beam_data = []

for ifc_beam in ifc_beams:
    csv_beam_guid = ifc_beam.GlobalId
    csv_beam_name = ifc_beam.Name
    # csv_beam_material = ifc_beam.Material
    # csv_beam_profile = ifc_beam.ProfileDefinition
    element_type = ifc_beam.is_a() # visszaadja az ifc osztály típusát, amit lekérdeztünk 10. sorban
    # element_check = None
    # if element_type == "IfcBeam" and csv_beam_name == "BEAM":
    #     element_check = "OK"
    # else:
    #     element_check = "Inconsistency"

    # csv_beam_length = None
    # try:
    #     csv_beam_length = ifc_beam.Representation.RepresentationItems[0].Items[0].Depth
    # except Exception:
    #     pass # if there is no data under the attribute, then 'pass'

    beam_data.append([csv_beam_guid, csv_beam_name, element_type])

# now, i'm having data extracted from ifc model
# Next step is creating a csv for ML model
# spreadsheet as pandas dataframe for furtherer operations
beam_dataframe = pandas.DataFrame(beam_data, columns=["GUID", "Name", "Type"])
# ellenőrzés a terminálon:
print(beam_dataframe)
# print(beam_dataframe.head(10)) # quick preview, displays only 10 rows if the dataframe

csv_dataframe = beam_dataframe.to_csv(r"..\data\processed\beam_data.csv", index=False) # wo row names
# az 'r' segít meggátolni a speciális string karakterkombók kezelését
# print(csv_dataframe) -> None
