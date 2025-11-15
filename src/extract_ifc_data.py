# import ifcopenshell # loads package for handling ifc files
# import pandas # loads package for handling data
# from ifcopenshell.util.element import MATERIAL_TYPE
# from pathlib import Path
# #
# # 7.4.2. Data Extraction
# # Open the IFC file, 'r' for reading
# ifc_path = Path("../data/input/OF3.ifc") # path to the IFC file within the project folder
# out_path = Path("../data/output/beam_data.csv")
#
# try:
#     ifc_model = ifcopenshell.open(ifc_path) # opens the file path and only opens the file path, does not parse it yet
#     print(f"IFC file path: {ifc_path}. Path is okay, the file is opened.")
# except Exception:
#     print("Error while opening the IFC file. Check the file path.")
#
# # stores the beams from the IFC model in a variable
# # ifc_beamsbyname = ifc_model.by_name("BEAM") # AttributeError: nincs ilyen attribútuma a
# ifc_beams = ifc_model.by_type("IfcBeam") # minden "IfcBeam"; tudjuk, hogy van ifcBeam => kell, hogy találjon
# number_of_beams = len(ifc_beams)
# if ifc_beams is None:
#     raise Exception("IFC file does not contain any beams.")
# else:
#     print(f"IFC file contains {number_of_beams} pieces of ifcBeam.")
#
# # csak egy üres lista, amihez hozzáfűzzük a kinyert ifc_beam-eket
# beam_data = []
#
# for ifc_beam in ifc_beams:
#     beam_guid = ifc_beam.GlobalId # GUID, # ez az az egyértelmű azonosító, amit a natív modellből kap az objektum, amikor létrehozzuk
#     element_type = ifc_beam.is_a() # visszaadja az ifc osztály típusát, amit lekérdeztünk 16. sorban
#     beam_name = ifc_beam.Name # Name, user provided name
#
#
#     # profile and length
#     ProfileName = None
#     Length = None
#     # Try Method 1: From representation
#     try:
#         if hasattr(ifc_beam, 'Representation') and ifc_beam.Representation:
#             for rep in ifc_beam.Representation.Representations:
#                 for item in rep.Items:
#                     # Try to get profile from SweptSolid
#                     if hasattr(item, 'SweptArea'):
#                         profile = item.SweptArea
#                         if hasattr(profile, 'ProfileName') and profile.ProfileName:
#                             ProfileName = profile.ProfileName
#                         elif hasattr(profile, 'Name') and profile.Name:
#                             ProfileName = profile.Name
#
#                     # Try to get profile directly
#                     if hasattr(item, 'Profile'):
#                         if hasattr(item.Profile, 'ProfileName') and item.Profile.ProfileName:
#                             ProfileName = item.Profile.ProfileName
#                         elif hasattr(item.Profile, 'Name') and item.Profile.Name:
#                             ProfileName = item.Profile.Name
#
#                     # Try to get length/depth
#                     if hasattr(item, 'Depth') and item.Depth:
#                         Length = item.Depth
#                     elif hasattr(item, 'DirectrixLength'):
#                         Length = item.DirectrixLength
#
#                     if ProfileName and Length:
#                         break
#                 if ProfileName and Length:
#                     break
#     except Exception:
#         pass
#
#         # Try Method 2: From type definition
#     if not ProfileName or not Length:
#         try:
#             if hasattr(ifc_beam, 'IsTypedBy') and ifc_beam.IsTypedBy:
#                 for rel in ifc_beam.IsTypedBy:
#                     beam_type = rel.RelatingType
#                     if hasattr(beam_type, 'RepresentationMaps'):
#                         for rep_map in beam_type.RepresentationMaps:
#                             mapped_rep = rep_map.MappedRepresentation
#                             for item in mapped_rep.Items:
#                                 if hasattr(item, 'SweptArea'):
#                                     profile = item.SweptArea
#                                     if not ProfileName:
#                                         if hasattr(profile, 'ProfileName') and profile.ProfileName:
#                                             ProfileName = profile.ProfileName
#                                         elif hasattr(profile, 'Name') and profile.Name:
#                                             ProfileName = profile.Name
#
#                                 if not Length:
#                                     if hasattr(item, 'Depth') and item.Depth:
#                                         Length = item.Depth
#         except Exception:
#             pass
#
#             # Try Method 3: From property sets
#             if not ProfileName or not Length:
#                 try:
#                     for rel in ifc_beam.IsDefinedBy:
#                         if rel.is_a("IfcRelDefinesByProperties"):
#                             pset = rel.RelatingPropertyDefinition
#                             if hasattr(pset, 'HasProperties'):
#                                 for prop in pset.HasProperties:
#                                     if not ProfileName and prop.Name in ['Profile', 'ProfileName', 'CrossSection']:
#                                         if hasattr(prop, 'NominalValue') and prop.NominalValue:
#                                             ProfileName = str(prop.NominalValue.wrappedValue)
#                                     if not Length and prop.Name in ['Length', 'Height', 'Depth']:
#                                         if hasattr(prop, 'NominalValue') and prop.NominalValue:
#                                             Length = float(prop.NominalValue.wrappedValue)
#                 except Exception:
#                     pass
#
#     # material and grade
#     MATERIAL_TYPE = None
#     MaterialName = None
#     MaterialGrade = None
#
#     try:
#         # egyszerű eset: közvetlen anyag-hozzárendelés
#         rels = [r for r in ifc_beam.HasAssociations if r.is_a("IfcRelAssociatesMaterial")]
#         if rels:
#             mat = rels[0].RelatingMaterial
#             if hasattr(mat, "Name"):
#                 Material = mat.Name
#     except Exception:
#         pass
#
#         # property setben keresünk anyagminőséget
#     try:
#         for rel in ifc_beam.IsDefinedBy:
#             if rel.is_a("IfcRelDefinesByProperties"):
#                 pset = rel.RelatingPropertyDefinition
#                 if hasattr(pset, "Name") and "Pset_MaterialSteel" in pset.Name:
#                     for prop in pset.HasProperties:
#                         if prop.Name == "StructuralGrade":
#                             StructuralGrade = prop.NominalValue.wrappedValue
#     except Exception:
#         pass
#
#         # --- 4.4 Assembly kapcsolat ---
#     AssemblyId = None
#     try:
#         for rel in ifc_beam.Decomposes:
#             if rel.is_a("IfcRelAggregates"):
#                 AssemblyId = rel.RelatingObject.GlobalId
#     except Exception:
#         pass
#
#     # --- 4.5 Kapcsolódó csavarok (IfcMechanicalFastener) ---
#     BoltCount = 0
#     try:
#         related = []
#         if hasattr(ifc_beam, "ConnectedFrom"):
#             related += ifc_beam.ConnectedFrom
#         if hasattr(ifc_beam, "ConnectedTo"):
#             related += ifc_beam.ConnectedTo
#         for rel in related:
#             if rel.is_a("IfcRelConnectsElements"):
#                 other = rel.RelatedElement
#                 if other.is_a("IfcMechanicalFastener"):
#                     BoltCount += 1
#     except Exception:
#         pass
#
#     # --- 4.6 Adatok tárolása ---
#     beam_data.append({
#         "GlobalId": beam_guid,
#         "Name": beam_name,
#         "Type": element_type,
#         "ProfileName": ProfileName,
#         "Length": Length,
#         "Material": Material,
#         # "StructuralGrade": StructuralGrade,
#         "AssemblyId": AssemblyId,
#         "BoltCount": BoltCount
#     })
#
# =============================================
#
# =============================================
# #  DataFrame létrehozása és mentés
# beam_dataframe = pandas.DataFrame(beam_data)
# out_path.parent.mkdir(parents=True, exist_ok=True)
# beam_dataframe.to_csv(out_path, index=False)
# print(f"Data exported to: {out_path}")
# print(beam_dataframe.head(number_of_beams))


    # beam_profile = ifc_beam.
    # beam_material = ifc_beam
    # beam_profile = ifc_beam.ProfileDefinition
    # element_check = None
    # if element_type == "IfcBeam" and beam_name == "BEAM":
    #     element_check = "OK"
    # else:
    #     element_check = "Inconsistency"

    # csv_beam_length = None
    # try:
    #     csv_beam_length = ifc_beam.Representation.RepresentationItems[0].Items[0].Depth
    # except Exception:
    #     pass # if there is no data under the attribute, then 'pass'

    # beam_data.append([beam_guid, beam_name, element_type])

# now, i'm having data extracted from ifc model
# Next step is creating a csv for ML model
# spreadsheet as pandas dataframe for furtherer operations
# beam_dataframe = pandas.DataFrame(beam_data, columns=["GUID", "Name", "Type"])
# ellenőrzés a terminálon:
# print(beam_dataframe)
# print(beam_dataframe.head(10)) # quick preview, displays only 10 rows if the dataframe
# csv_dataset = beam_dataframe.to_csv(r"..\data\output\beam_data.csv", index=False) # wo row name=index
# az 'r' segít meggátolni a speciális string karakterkombók kezelését
# print(csv_dataset) -> None
# =============================================
#
# =============================================

# import ifcopenshell  # loads package for handling ifc files
# import pandas  # loads package for handling data
# from pathlib import Path
# import sys
#
# # 7.4.2. Data Extraction
# # Open the IFC file, 'r' for reading
# ifc_path = Path("../data/input/OF3.ifc")  # path to the IFC file within the project folder
# out_path = Path("../data/output/beam_data.csv")
#
# try:
#     ifc_model = ifcopenshell.open(
#         str(ifc_path))  # opens the file path and only opens the file path, does not parse it yet
#     print(f"IFC file path: {ifc_path}. Path is okay, the file is opened.")
# except FileNotFoundError:
#     print(f"Error: IFC file not found at path: {ifc_path}")
#     print(f"Please check if the file exists at this location.")
#     sys.exit(1)
# except Exception as e:
#     print(f"Error while opening the IFC file: {e}")
#     sys.exit(1)
#
# # stores the beams from the IFC model in a variable
# ifc_beams = ifc_model.by_type("IfcBeam")  # minden "IfcBeam"; tudjuk, hogy van ifcBeam => kell, hogy találjon
# number_of_beams = len(ifc_beams)
# if ifc_beams is None or number_of_beams == 0:
#     print("IFC file does not contain any beams.")
#     sys.exit(1)
# else:
#     print(f"IFC file contains {number_of_beams} pieces of ifcBeam.")
#
# # Debug: Print structure of first beam
# print("\n=== DEBUGGING FIRST BEAM ===")
# first_beam = ifc_beams[0]
# print(f"Beam Name: {first_beam.Name}")
# print(f"Beam GUID: {first_beam.GlobalId}")
#
# # Check quantities
# print("\nChecking IsDefinedBy relationships:")
# if hasattr(first_beam, 'IsDefinedBy'):
#     for rel in first_beam.IsDefinedBy:
#         print(f"  Relationship: {rel.is_a()}")
#         if rel.is_a("IfcRelDefinesByProperties"):
#             pset = rel.RelatingPropertyDefinition
#             print(f"    PropertySet Name: {pset.Name if hasattr(pset, 'Name') else 'N/A'}")
#             if pset.is_a("IfcElementQuantity"):
#                 print(f"    This is a Quantity Set!")
#                 for quantity in pset.Quantities:
#                     print(f"      Quantity: {quantity.Name} = {quantity}")
#                     if hasattr(quantity, 'LengthValue'):
#                         print(f"        LengthValue: {quantity.LengthValue}")
#             elif hasattr(pset, 'HasProperties'):
#                 for prop in pset.HasProperties:
#                     print(
#                         f"      Property: {prop.Name} = {prop.NominalValue if hasattr(prop, 'NominalValue') else 'N/A'}")
#
# # Check representation
# print("\nChecking Representation:")
# if hasattr(first_beam, 'Representation') and first_beam.Representation:
#     print(f"  Has Representation: Yes")
#     for rep in first_beam.Representation.Representations:
#         print(f"    Representation Type: {rep.RepresentationType}")
#         print(f"    Representation Identifier: {rep.RepresentationIdentifier}")
#         for item in rep.Items:
#             print(f"      Item Type: {item.is_a()}")
#             print(f"      Item: {item}")
#             if hasattr(item, 'SweptArea'):
#                 print(f"        SweptArea: {item.SweptArea.is_a()}")
#                 print(f"        SweptArea Attributes: {dir(item.SweptArea)}")
#                 if hasattr(item.SweptArea, 'ProfileName'):
#                     print(f"        ProfileName: {item.SweptArea.ProfileName}")
#                 if hasattr(item.SweptArea, 'ProfileType'):
#                     print(f"        ProfileType: {item.SweptArea.ProfileType}")
#             if hasattr(item, 'Depth'):
#                 print(f"        Depth: {item.Depth}")
#             if hasattr(item, 'Profile'):
#                 print(f"        Profile: {item.Profile}")
#
# # Check object type
# print("\nChecking ObjectType:")
# if hasattr(first_beam, 'ObjectType'):
#     print(f"  ObjectType: {first_beam.ObjectType}")
#
# # Check type
# print("\nChecking IsTypedBy:")
# if hasattr(first_beam, 'IsTypedBy'):
#     for rel in first_beam.IsTypedBy:
#         beam_type = rel.RelatingType
#         print(f"  Type: {beam_type.Name if hasattr(beam_type, 'Name') else 'N/A'}")
#
# print("\n=== END DEBUG ===\n")
#
# # csak egy üres lista, amihez hozzáfűzzük a kinyert ifc_beam-eket
# beam_data = []
#
# for ifc_beam in ifc_beams:
#     beam_guid = ifc_beam.GlobalId  # GUID
#     element_type = ifc_beam.is_a()  # visszaadja az ifc osztály típusát
#     beam_name = ifc_beam.Name  # Name, user provided name
#
#     # profile and length
#     ProfileName = None
#     Length = None
#
#     # Try from ObjectType (common in Tekla exports)
#     if hasattr(ifc_beam, 'ObjectType') and ifc_beam.ObjectType:
#         ProfileName = ifc_beam.ObjectType
#
#     # Try from element quantities
#     try:
#         for rel in ifc_beam.IsDefinedBy:
#             if rel.is_a("IfcRelDefinesByProperties"):
#                 pset = rel.RelatingPropertyDefinition
#                 if pset.is_a("IfcElementQuantity"):
#                     for quantity in pset.Quantities:
#                         # Look for length-related quantities
#                         if quantity.Name in ['Length', 'Width', 'Height'] and hasattr(quantity, 'LengthValue'):
#                             if quantity.Name == 'Width' and not Length:
#                                 Length = quantity.LengthValue
#     except Exception as e:
#         pass
#
#     # Try from representation
#     try:
#         if hasattr(ifc_beam, 'Representation') and ifc_beam.Representation:
#             for rep in ifc_beam.Representation.Representations:
#                 for item in rep.Items:
#                     # Check for MappedItem (common in assemblies)
#                     if item.is_a('IfcMappedItem'):
#                         mapped_rep = item.MappingSource.MappedRepresentation
#                         for mapped_item in mapped_rep.Items:
#                             if hasattr(mapped_item, 'SweptArea'):
#                                 profile = mapped_item.SweptArea
#                                 if not ProfileName and hasattr(profile, 'ProfileName') and profile.ProfileName:
#                                     ProfileName = profile.ProfileName
#                             if hasattr(mapped_item, 'Depth') and not Length:
#                                 Length = mapped_item.Depth
#
#                     # Check for direct SweptSolid
#                     if hasattr(item, 'SweptArea'):
#                         profile = item.SweptArea
#                         if not ProfileName and hasattr(profile, 'ProfileName') and profile.ProfileName:
#                             ProfileName = profile.ProfileName
#
#                     if hasattr(item, 'Depth') and not Length:
#                         Length = item.Depth
#     except Exception as e:
#         pass
#
#     # material and grade
#     Material = None
#     StructuralGrade = None
#
#     try:
#         # egyszerű eset: közvetlen anyag-hozzárendelés
#         rels = [r for r in ifc_beam.HasAssociations if r.is_a("IfcRelAssociatesMaterial")]
#         if rels:
#             mat = rels[0].RelatingMaterial
#             if hasattr(mat, "Name"):
#                 Material = mat.Name
#     except Exception:
#         pass
#
#     # property setben keresünk anyagminőséget
#     try:
#         for rel in ifc_beam.IsDefinedBy:
#             if rel.is_a("IfcRelDefinesByProperties"):
#                 pset = rel.RelatingPropertyDefinition
#                 if hasattr(pset, "Name") and pset.Name and "Pset_MaterialSteel" in pset.Name:
#                     for prop in pset.HasProperties:
#                         if prop.Name == "StructuralGrade":
#                             StructuralGrade = prop.NominalValue.wrappedValue
#     except Exception:
#         pass
#
#     # --- 4.4 Assembly kapcsolat ---
#     AssemblyId = None
#     try:
#         for rel in ifc_beam.Decomposes:
#             if rel.is_a("IfcRelAggregates"):
#                 AssemblyId = rel.RelatingObject.GlobalId
#     except Exception:
#         pass
#
#     # --- 4.5 Kapcsolódó csavarok (IfcMechanicalFastener) ---
#     BoltCount = 0
#     try:
#         related = []
#         if hasattr(ifc_beam, "ConnectedFrom"):
#             related += ifc_beam.ConnectedFrom
#         if hasattr(ifc_beam, "ConnectedTo"):
#             related += ifc_beam.ConnectedTo
#         for rel in related:
#             if rel.is_a("IfcRelConnectsElements"):
#                 other = rel.RelatedElement
#                 if other.is_a("IfcMechanicalFastener"):
#                     BoltCount += 1
#     except Exception:
#         pass
#
#     # --- 4.6 Adatok tárolása ---
#     beam_data.append({
#         "GlobalId": beam_guid,
#         "Name": beam_name,
#         "Type": element_type,
#         "ProfileName": ProfileName,
#         "Length": Length,
#         "Material": Material,
#         "StructuralGrade": StructuralGrade,
#         "AssemblyId": AssemblyId,
#         "BoltCount": BoltCount
#     })
#
# #  DataFrame létrehozása és mentés
# beam_dataframe = pandas.DataFrame(beam_data)
# out_path.parent.mkdir(parents=True, exist_ok=True)
# beam_dataframe.to_csv(out_path, index=False)
# print(f"✅ Data exported to: {out_path}")
# print(f"\nFirst 10 rows:")
# print(beam_dataframe.head(10))

import ifcopenshell  # loads package for handling ifc files
import pandas  # loads package for handling data
from pathlib import Path
import sys

# 7.4.2. Data Extraction
# Open the IFC file, 'r' for reading
ifc_path = Path("../data/input/ifc/OF3.ifc")  # path to the IFC file within the project folder
out_path = Path("../data/output/beam_data_a9.csv")

try:
    ifc_model = ifcopenshell.open(
        str(ifc_path))  # opens the file path and only opens the file path, does not parse it yet
    print(f"IFC file path: {ifc_path}. Path is okay, the file is opened.")
except FileNotFoundError:
    print(f"Error: IFC file not found at path: {ifc_path}")
    print(f"Please check if the file exists at this location.")
    sys.exit(1)
except Exception as e:
    print(f"Error while opening the IFC file: {e}")
    sys.exit(1)

# stores the beams from the IFC model in a variable
ifc_beams = ifc_model.by_type("IfcBeam")  # minden "IfcBeam"; tudjuk, hogy van ifcBeam => kell, hogy találjon
number_of_beams = len(ifc_beams)
if ifc_beams is None or number_of_beams == 0:
    print("IFC file does not contain any beams.")
    sys.exit(1)
else:
    print(f"IFC file contains {number_of_beams} pieces of ifcBeam.")

# csak egy üres lista, amihez hozzáfűzzük a kinyert ifc_beam-eket
beam_data = []

for ifc_beam in ifc_beams:
    beam_guid = ifc_beam.GlobalId  # GUID
    element_type = ifc_beam.is_a()  # visszaadja az ifc osztály típusát
    beam_name = ifc_beam.Name  # Name, user provided name

    # profile and length
    ProfileName = None
    Length = None
    Width = None
    Height = None

    # Try from Tekla-specific property sets and BaseQuantities
    try:
        for rel in ifc_beam.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition

                # Check if it's an element quantity (BaseQuantities)
                if pset.is_a("IfcElementQuantity"):
                    for quantity in pset.Quantities:
                        if quantity.Name == 'Length' and hasattr(quantity, 'LengthValue'):
                            if not Length:
                                Length = quantity.LengthValue
                        elif quantity.Name == 'Width' and hasattr(quantity, 'LengthValue'):
                            if not Width:
                                Width = quantity.LengthValue
                        elif quantity.Name == 'Height' and hasattr(quantity, 'LengthValue'):
                            if not Height:
                                Height = quantity.LengthValue

                # Check Tekla Quantity property set
                elif hasattr(pset, 'HasProperties'):
                    if hasattr(pset, 'Name') and pset.Name == 'Tekla Quantity':
                        for prop in pset.HasProperties:
                            if prop.Name == 'Length' and hasattr(prop, 'NominalValue'):
                                if not Length:
                                    Length = prop.NominalValue.wrappedValue
                            elif prop.Name == 'Width' and hasattr(prop, 'NominalValue'):
                                if not Width:
                                    Width = prop.NominalValue.wrappedValue
                            elif prop.Name == 'Height' and hasattr(prop, 'NominalValue'):
                                if not Height:
                                    Height = prop.NominalValue.wrappedValue
    except Exception:
        pass

    # For ProfileName, try to construct from Width x Height if available
    if not ProfileName and Width and Height:
        ProfileName = f"{Width}x{Height}"

    # Try from ObjectType (some exporters use this)
    if not ProfileName and hasattr(ifc_beam, 'ObjectType') and ifc_beam.ObjectType:
        ProfileName = ifc_beam.ObjectType

    # material and grade
    Material = None
    StructuralGrade = None

    try:
        # egyszerű eset: közvetlen anyag-hozzárendelés
        rels = [r for r in ifc_beam.HasAssociations if r.is_a("IfcRelAssociatesMaterial")]
        if rels:
            mat = rels[0].RelatingMaterial
            if hasattr(mat, "Name"):
                Material = mat.Name
    except Exception:
        pass

    # property setben keresünk anyagminőséget
    try:
        for rel in ifc_beam.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if hasattr(pset, "Name") and pset.Name and "Pset_MaterialSteel" in pset.Name:
                    for prop in pset.HasProperties:
                        if prop.Name == "StructuralGrade":
                            StructuralGrade = prop.NominalValue.wrappedValue
    except Exception:
        pass

    # --- 4.4 Assembly kapcsolat ---
    AssemblyId = None
    try:
        for rel in ifc_beam.Decomposes:
            if rel.is_a("IfcRelAggregates"):
                AssemblyId = rel.RelatingObject.GlobalId
    except Exception:
        pass

    # --- 4.5 Kapcsolódó csavarok (IfcMechanicalFastener) ---
    BoltCount = 0
    try:
        related = []
        if hasattr(ifc_beam, "ConnectedFrom"):
            related += ifc_beam.ConnectedFrom
        if hasattr(ifc_beam, "ConnectedTo"):
            related += ifc_beam.ConnectedTo
        for rel in related:
            if rel.is_a("IfcRelConnectsElements"):
                other = rel.RelatedElement
                if other.is_a("IfcMechanicalFastener"):
                    BoltCount += 1
    except Exception:
        pass

    # --- 4.6 Adatok tárolása ---
    beam_data.append({
        "GlobalId": beam_guid,
        "Name": beam_name,
        "Type": element_type,
        "ProfileName": ProfileName,
        "Length": Length,
        "Material": Material,
        "StructuralGrade": StructuralGrade,
        "AssemblyId": AssemblyId,
        "BoltCount": BoltCount # hibás
    })

#  DataFrame létrehozása és mentés
beam_dataframe = pandas.DataFrame(beam_data)
out_path.parent.mkdir(parents=True, exist_ok=True)
beam_dataframe.to_csv(out_path, index=False)
print(f"✅ Data exported to: {out_path}")
print(f"\nFirst 10 rows:")
print(beam_dataframe.head(10))