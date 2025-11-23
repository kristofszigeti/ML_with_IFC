"""
Tehát a Tekla-IFC NEM IfcRelConnectsElements-szel köti össze a csavar–lemez–gerenda kapcsolatot,
hanem assemblies + aggregálás logikát használ:
    van egy IfcElementAssembly (pl. egy csomópont / kapcsolati egység),
        ahhoz IfcRelAggregates köti hozzá a gyerekeket:
            lemezek (IfcPlate),
            csavarok (IfcMechanicalFastener),
            esetleg gerendák/memberek.
Pont emiatt nem kell általános extractor, elég ez az 1 AXIÓMA:
    !!! „Olyan IfcPlate érdekel, amely ugyanabban az assembly-ben van, mint egy vagy több IfcMechanicalFastener.”
Ebből már tudunk nagyon konkrét, célzott extraktort írni.
Következő apró lépés: bizonyítsuk, hogy tényleg így vannak összerakva
Most NEM extraktort írunk még,
csak megnézzük 3–5 assemblyt, hogy hogy néz ki belül.
"""

import ifcopenshell
from pathlib import Path

ifc_path = Path("../"
                "../data/input/ifc/Skyline 2.ifc")
str_model = ifcopenshell.open(ifc_path)

# We go through the assemblies
assemblies = str_model.by_type("IfcElementAssembly") # this is a list
print(f"Number of assemblies: {len(assemblies)} pcs") # so it has a length

# These are a sample
print("\n === Assembly ===")
for assembly in assemblies[:5]:
    # if assembly.Tag == "A/27":# [:5] is a list operation on a list: only the first 5 assemblies are printed
        print("GUID:", assembly.GlobalId, "Name:", assembly.Name, "Tag:", assembly.Tag)

        # We look for corresponding IfcRelAggregates connections
        relations = [rel for rel in str_model.by_type("IfcRelAggregates") if rel.RelatingObject == assembly]
        # print(relations)

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

        print(f"Plates: {len(plates)} pcs | Fasteners: {len(fasteners)} pcs")

        if plates:
            print(2 * " " + "Connected plates:")
            print(plates)
        if fasteners:
            print(2 * " " + "Connected fasteners:")
            for fastener in fasteners:
                print(f"   {fastener.GlobalId}")
            print()
        else:
            print()

print("Done.")


