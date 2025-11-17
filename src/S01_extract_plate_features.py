"""Konkrét, ÚJ lépés: extract_plate_features.py

Fogjuk a mostani inspect_assemblies.py logikát, és:

nem printelünk,

hanem táblázatot építünk, soronként 1 lemez + hozzá bolt_count.

Mit fog tartalmazni a tábla?

Sor = egy plate az IFC-ből:

PlateGlobalId

AssemblyGlobalId

AssemblyName (pl. „BEAM”, „CONNECTION…”)

(opcionálisan AssemblyTag)

bolt_count = hány IfcMechanicalFastener volt ugyanabban az assembly-ben

Ez lesz a valódi ML input a mostani placeholder Feature=1 helyett.
"""

import ifcopenshell
from pathlib import Path
import pandas

# 1 INPUT
ifc_path = Path("../data/input/ifc/OF3.ifc")
str_model = ifcopenshell.open(ifc_path)

# 2 READ-IN: Assemblies + RelAggregates
assemblies = str_model.by_type("IfcElementAssembly")
rel_aggregates = str_model.by_type("IfcRelAggregates")

print(f"Number of assemblies: {len(assemblies)} pcs.")
print(f"Number of IfcRelAggregates: {len(rel_aggregates)} pcs.")

rows = []

for assembly in assemblies:
    # Az assembly-hez tartozó aggregáló relációk, Corresponding aggregating relations
    relations = [rel for rel in rel_aggregates if rel.RelatingObject == assembly]

    plates = []
    fasteners = []

    for relation in relations:
        for child in relation.RelatedObjects:
            if child.is_a("IfcPlate"):
                plates.append(child)
            elif child.is_a("IfcMechanicalFastener"):
                fasteners.append(child)
            else:
                continue


    if not plates:
        continue # skips the assembly if there are no plates = skips the rest of the loop

    bolt_count = len(fasteners)

    # one row per plate
    for plate in plates:
        rows.append({
            "Plate_GUID": plate.GlobalId,
            "Assembly_GUID": assembly.GlobalId,
            "Assembly_Name": assembly.Name,
            "Assembly_Tag": assembly.Tag,
            "bolt_count": bolt_count,
        })

# 3 SAVE - DATAFRAME
dataframe = pandas.DataFrame(rows)
print(dataframe.head())

output_path = Path("../data/output/csv_dataframe/plate_features.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
csv_dataset = dataframe.to_csv(output_path, index=False)

print(f"Plate features saved to: {output_path}")
print("Bolt count stats:")
print(dataframe["bolt_count"].describe())
# count  = 186
# mean   = 5.8
# std    = 8.20   → nagyon szór
# min    = 0      → vannak MISSING csavarok (hibás/hiányos)
# 25%    = 1      → vannak kevés csavaros lemezek
# 50%    = 2      → medián csak 2 csavar (!)
# 75%    = 6      → a „normális” tartomány valószínűleg itt kezdődik
# max    = 26     → extrém sok csavar (jó eséllyel outlier)
# ✔ vannak valódi outlierek alul
#
# bolt_count = 0
#
# bolt_count = 1
#
# bolt_count = 2
#
# ✔ vannak valódi outlierek felül
#
# bolt_count = 20–26
#
# ✔ a középsáv valószínűleg 4–10 körül van
#
# Ez a kész feature-tér.

