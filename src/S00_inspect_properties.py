import ifcopenshell
import ifcopenshell.util.element
from pathlib import Path
import pprint  # Szép kiíratáshoz

# 1. Fájl elérési útja (ezt írd át a te fájlodra!)
ifc_path = Path("../data/input/ifc/740PWH.ifc")

print(f"Loading {ifc_path}...")
model = ifcopenshell.open(ifc_path)

# 2. Keressünk egy Gerendát (IfcBeam) - mivel a képen is az van
beams = model.by_type("IfcBeam")

if not beams:
    print("Nem találtam IfcBeam elemet a fájlban!")
else:
    # Vegyük az elsőt mintának
    test_element = beams[0]

    print(f"\n=== Vizsgált elem: {test_element.Name} (GUID: {test_element.GlobalId}) ===")

    # 3. Kérjük le az ÖSSZES Property Set-et
    # Ez a varázsfüggvény kigyűjti az összes tulajdonságot egy Python szótárba
    psets = ifcopenshell.util.element.get_psets(test_element)

    # 4. Listázzuk ki a Pset neveket, hogy lássuk, mi létezik
    print("\nElérhető Property Set-ek (csoportok):")
    print(list(psets.keys()))

    # 5. Keressük a "CalculatedGeometryValues"-t vagy hasonlót
    # target_pset = "CalculatedGeometryValues"
    target_pset = "BaseQuantities"

    # SHOW the content generally
    pprint.pprint(psets)

    if target_pset in psets:
        print(f"\n✅ MEGTALÁLTAM! A '{target_pset}' létezik az IFC-ben!")
        print("Tartalma:")
        pprint.pprint(psets[target_pset])
    else:
        print(f"\n❌ A '{target_pset}' NEM létezik közvetlenül az IFC fájlban.")
        print("Ez azt jelenti, hogy a Trimble Connect számolja ki valós időben.")

        # Nézzük meg, van-e máshol koordináta (pl. Tekla Quantity-ben)
        if "Tekla Quantity" in psets:
            print("\nViszont találtam 'Tekla Quantity'-t! Ennek tartalma:")
            pprint.pprint(psets["Tekla Quantity"])
            # pprint.pprint(psets)