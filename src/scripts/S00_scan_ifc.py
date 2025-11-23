"""
Egy általános, „mindent kinyerő” IFC-extractor fél iparágnyi meló.

Egy szűk feladatra kihegyezett extractor (pl. “IfcPlate + hozzárendelt csavarok száma”) teljesen reális, és belefér MSc-be – ha leszűkítjük a scope-ot.
„Lemezek, amelyekhez furat/csavar tartozik → ezekre anomáliadetektálás, pontozás.”
Ez tökéletes, nagyon konkrét use-case.
Nem kell „bármit bármiből” kinyerni, csak: Plate + Fastener kapcsolat.
Mit kell ehhez valójában tudni?
Két szint:
Elméleti IFC-szint (nagyon röviden)
    Lemez: IfcPlate
    Csavar: IfcFastener vagy IfcMechanicalFastener (Tekla-függő).
    Kapcsolat elemek között: tipikusan
    IfcRelConnectsElements
    vagy IfcRelConnectsWithRealizingElements
    esetleg assembly-n keresztül: IfcElementAssembly + IfcRelAggregates.
Cél:
    megtalálni azt a mintát a TE IFC-dben, hogy
    „melyik reláció köti össze az IfcPlate-et és a csavar/fastener elemet”.
    Ehhez viszont nem kell feltalálni az IFC-t, csak le kell kérdezni, hogy a te modelljeidben konkrétan mi van.
    Következő lépés: NE extractor még, csak FELDERÍTÉS
    Apró, teljesen ártalmatlan script, ami csak statisztikát ír ki:
Cél most:
    Van-e a modellben: IfcPlate, IfcFastener, IfcMechanicalFastener.
    Milyen relációk vannak jelen: IfcRelConnectsElements, IfcRelConnectsWithRealizingElements, IfcRelAggregates stb.
    Ezekből hány darab van – hogy lássuk, miből érdemes elindulni.
"""

import ifcopenshell
from pathlib import Path
from collections import Counter # this is for counting the elements

ifc_name = "740PWH.ifc"

ifc_path = Path(f"../../data/input/ifc/{ifc_name}")
str_model = ifcopenshell.open(ifc_path)

# 1) Elem-típusok darabszáma
types = [element.is_a() for element in str_model]
type_counts = Counter(types)
# print(type_counts) # Counter({'IfcCartesianPoint': 39988, 'IfcPolyLoop': 24028, ...})

print(f"{'=== Element type counts (most_common(n=None)) === ':^50}")
print(f"{'Type':^40s}| Count")
for type, count in type_counts.most_common():
# for type, count in type_counts.items():
    print(f"{type:40s}: {count}")

print(f"\n{'=== RELATION TYPES IN THIS SPECIFIC IFC FILE ===':^60}")
for relation_type in ["ifcRelConnectsElements", # means "is connected to"
                      "ifcRelConnectsWithRealizingElements", # means "is connected to"
                      "ifcRelAggregates", # means "is part of"
                      "ifcRelAssociates"]: # means "is associated with"
    relations = str_model.by_type(relation_type)
    print(f"{f'Number of {relation_type} relations:':57s} {len(relations)} db")

print("Done.")