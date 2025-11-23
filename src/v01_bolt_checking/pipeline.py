# import ifcopenshell                      # IFC modell beolvasására
# import pandas as pd                      # Táblázatos adatok kezelésére
# from pathlib import Path                 # Elérési utak kezelésére
# from sklearn.ensemble import IsolationForest   # Anomáliadetektáló modell
# from joblib import dump                  # Modell mentéséhez (opcionális)
#
# # STREAMLIT BACKGROUND LOGIC => AFTER ANY CHANGE TERMINAL NEEDS TO BE CLOSED AND RESTARTED AGAIN!!
# ## 1st EXPERIMENT
# # 1 PLate + bolt extraction out of the IFC file
# def extract_plate_features_from_ifc(ifc_path: Path) -> pd.DataFrame:
#     """
#        Beolvassa az IFC-t és visszaadja a Plate + bolt_count táblát.
#     """
#     model = ifcopenshell.open(ifc_path)  # IFC modell betöltése
#
#     assemblies = model.by_type("IfcElementAssembly")  # Minden assembly kigyűjtése
#     rel_aggregates = model.by_type("IfcRelAggregates")  # Assembly–gyerek kapcsolatok
#
#     rows = []  # Ebbe gyűjtjük az eredménysorokat
#
#     for assembly in assemblies:  # Végigmegyünk az összes assembly-n
#         relations = [  # Kiválogatjuk a kapcsolódó RelAggregates relációkat
#             rel for rel in rel_aggregates
#             if rel.RelatingObject == assembly
#         ]
#
#         plates = []  # Az adott assembly lemezei
#         fasteners = []  # Az adott assembly csavarjai
#
#         for rel in relations:  # Végigmegyünk az adott assembly kapcsolataiin
#             for child in rel.RelatedObjects:  # Végigmegyünk a kapcsolt gyerek-elemeken
#                 if child.is_a("IfcPlate"):  # Ha lemez
#                     plates.append(child)  # → hozzáadjuk a plates listához
#                 elif child.is_a("IfcMechanicalFastener"):  # Ha csavar
#                     fasteners.append(child)  # → hozzáadjuk a csavarlistához
#
#         if not plates:  # Ha nincs plate, lépünk a következő assembly-re
#             continue
#
#         bolt_count = len(fasteners)  # Csavarok száma ebben az assembly-ben
#
#         for plate in plates:  # Minden plate-hez külön sor
#             rows.append({
#                 "PlateGlobalId": plate.GlobalId,  # Plate azonosítója
#                 "AssemblyGlobalId": assembly.GlobalId,  # Assembly azonosítója
#                 "AssemblyName": assembly.Name,  # Assembly neve
#                 "AssemblyTag": assembly.Tag,  # Tekla Tag (pl. A/213)
#                 "bolt_count": bolt_count  # Csavarok száma
#             })
#
#     df = pd.DataFrame(rows)  # Sorokból DataFrame
#     return df  # Visszaadjuk a plate_features táblát
#
# # 2) Anomáliadetektálás bolt_count alapján
# def run_anomaly_on_plate_features(df_plate: pd.DataFrame,
#                                   contamination: float = 0.05,
#                                   save_model_path: Path | None = None) -> pd.DataFrame:
#     """
#     IsolationForest futtatása a bolt_count oszlopon.
#     Visszaad egy DataFrame-et anomaly_score és anomaly_label oszlopokkal.
#     """
#     df = df_plate.copy()                             # Másolat, hogy ne írjuk felül az eredetit
#
#     X = df[["bolt_count"]].copy()                    # Csak a bolt_count mint numerikus feature
#     X["bolt_count"] = pd.to_numeric(                 # Biztosítjuk, hogy szám legyen
#         X["bolt_count"], errors="coerce"
#     )
#
#     mask = X["bolt_count"].notna()                   # Maszk: ahol érvényes a bolt_count
#     X_used = X.loc[mask].reset_index(drop=True)      # Csak használható sorok a modellhez
#     df_used = df.loc[mask].reset_index(drop=True)    # Ugyanezek a plate sorok metaadatokkal
#
#     model = IsolationForest(                         # IsolationForest modell példányosítása
#         n_estimators=200,                            # Fák száma
#         contamination=contamination,                 # Várt anomáliaarány
#         random_state=42                              # Reprodukálhatóság
#     )
#
#     model.fit(X_used)                                # Modell tanítása a bolt_count adatra
#
#     labels = model.predict(X_used)                   # +1 = normál, -1 = anomália címkék
#     scores = model.decision_function(X_used)         # Folytonos anomália-pontszámok
#
#     df_used["anomaly_score"] = scores                # Pontszám hozzáadása a táblához
#     df_used["anomaly_label"] = labels                # Címke hozzáadása a táblához
#
#     if save_model_path is not None:                  # Ha megadtunk modell mentési útvonalat
#         save_model_path.parent.mkdir(parents=True, exist_ok=True)  # Mappa biztosítása
#         dump(model, save_model_path)                 # Modell mentése .pkl fájlba
#
#     return df_used                                   # Visszaadjuk a plate + anomaly eredményeket
#
# # 3) Teljes pipeline egyben: IFC → plate_features → anomaly eredmények
# def run_full_pipeline(ifc_path: Path,
#                       contamination: float = 0.05,
#                       save_model_path: Path | None = None) -> pd.DataFrame:
#     # IN-BETWEEN CHECK
#     model = ifcopenshell.open(ifc_path)
#
#     # CHECK if IfcRelAggregates count and existence
#     has_rel_aggregates = model.by_type("IfcRelAggregates")
#     if len(has_rel_aggregates) < 10: # less than 10 record is undeniably too low in case of a structure; >100, >1000 is relevant
#         raise ValueError(
#             "The IFC file does not contain sufficient assembly-level relations "
#             "(IfcRelAggregates). Bolt–hole anomaly detection cannot be performed "
#             "on this export."
#         )
#     """
#     Teljes folyamat egy lépésben:
#     IFC beolvasás → Plate + bolt_count extrakció → anomáliadetektálás.
#     Visszatér: DataFrame a plate-ekkel és anomália eredményekkel.
#     """
#     df_plate = extract_plate_features_from_ifc(ifc_path)   # Plate + bolt_count kinyerése
#     df_result = run_anomaly_on_plate_features(             # Anomáliák számítása
#         df_plate,
#         contamination=contamination,
#         save_model_path=save_model_path
#     )
#     return df_result                                       # Visszaadjuk az eredményt az UI-nak vagy további feldolgozásnak


"""#### NEW APPROACH: DISTINGUISHED EXTRACTION ####"""
## 2nd EXPERIMENT
import ifcopenshell                                      # IFC model reading
import ifcopenshell.util.element as Element              # Helper for reading property sets (psets)
import pandas as pd                                      # Tabular data handling
from pathlib import Path                                 # Filesystem paths
from sklearn.ensemble import IsolationForest             # Unsupervised anomaly detection model
from joblib import dump                                  # Model serialization (optional)


def extract_element_features_from_ifc(ifc_path: Path,
                                      element_type: str) -> pd.DataFrame:
    """
    Extracts basic geometric and metadata features for a given element type
    from a Tekla-exported IFC model.

    element_type: 'plate', 'beam', or 'column'
    returns: DataFrame with one row per element and numeric features per row
    """

    model = ifcopenshell.open(ifc_path)                  # Load IFC model into memory

    # --- 1) Map element_type string to IFC class name(s) ---
    if element_type.lower() == "plate":
        ifc_classes = ["IfcPlate"]                       # Plates
    elif element_type.lower() == "beam":
        ifc_classes = ["IfcBeam", "IfcMember"]           # Beams / secondary members
    elif element_type.lower() == "column":
        ifc_classes = ["IfcColumn", "IfcMember"]         # Columns / vertical members
    else:
        raise ValueError(f"Unsupported element_type: {element_type}")

    elements = []                                        # List to collect all elements of the selected type
    for cls in ifc_classes:
        elements.extend(model.by_type(cls))              # Append all instances of each IFC class

    rows = []                                            # Rows for the resulting DataFrame

    for el in elements:
        psets = Element.get_psets(el)                    # Read all property sets for the element

        # --- 2) Generic identifiers ---
        guid = getattr(el, "GlobalId", None)            # GlobalId as unique identifier
        name = getattr(el, "Name", None)                # Name field from IFC entity
        tag = getattr(el, "Tag", None)                  # Tag (often Tekla part mark or GUID-like string)

        # --- 3) Tekla / dn_Part properties (if available) ---
        dn_part = psets.get("dn_Part", {})               # dn_Part property set from Tekla
        part_pos = dn_part.get("PART_POS", None)         # Tekla part position (e.g. 'CC5L/147')
        assembly_pos = dn_part.get("ASSEMBLY_POS", None) # Tekla assembly position (e.g. 'CC5A/190')
        perimeter = dn_part.get("PERIMETER", None)       # Perimeter (useful for plates)

        # --- 4) Tekla Quantity (geometric measures) ---
        tekla_qty = psets.get("Tekla Quantity", {})      # Geometric/quantity info from Tekla
        weight = tekla_qty.get("Weight", None)           # Element weight
        height = tekla_qty.get("Height", None)           # Height (can be thickness or profile depth)
        width = tekla_qty.get("Width", None)             # Width (profile or plate dimension)
        length = tekla_qty.get("Length", None)           # Length (main element length)
        net_surface_area = tekla_qty.get("Net surface area", None)  # Surface area if available
        gross_footprint_area = tekla_qty.get("Gross footprint area", None)  # Footprint if available

        # --- 5) Element-type specific additional properties ---
        load_bearing = None                              # Default for all element types

        if element_type.lower() == "plate":
            plate_pset = psets.get("Pset_PlateCommon", {})
            load_bearing = plate_pset.get("LoadBearing", None)
            reference = plate_pset.get("Reference", None)
        elif element_type.lower() == "beam":
            beam_pset = psets.get("Pset_BeamCommon", {})
            load_bearing = beam_pset.get("LoadBearing", None)
            reference = beam_pset.get("Reference", None)
        elif element_type.lower() == "column":
            col_pset = psets.get("Pset_ColumnCommon", {})
            load_bearing = col_pset.get("LoadBearing", None)
            reference = col_pset.get("Reference", None)
        else:
            reference = None                             # Fallback, should not happen

        # --- 6) Construct a row for this element ---
        row = {
            "ElementType": element_type.lower(),         # plate / beam / column
            "IFCClass": el.is_a(),                       # Actual IFC class name (e.g. IfcBeam)
            "GlobalId": guid,                            # Unique IFC identifier
            "Name": name,                                # Element name
            "Tag": tag,                                  # Tekla Tag (if exported)

            "PART_POS": part_pos,                        # Tekla part position
            "ASSEMBLY_POS": assembly_pos,                # Tekla assembly position
            "Reference": reference,                      # Common reference from Pset_*Common

            "Perimeter": perimeter,                      # Perimeter (mainly for plates)
            "Weight": weight,                            # Weight from Tekla Quantity
            "Height": height,                            # Height (thickness or profile depth)
            "Width": width,                              # Width (plate width or profile width)
            "Length": length,                            # Length (element span / height)
            "NetSurfaceArea": net_surface_area,          # Net surface area
            "GrossFootprintArea": gross_footprint_area,  # Footprint area

            "LoadBearing": load_bearing,                 # Load-bearing flag (if available)
        }

        rows.append(row)                                 # Add row to list

    df = pd.DataFrame(rows)                             # Build DataFrame from collected rows
    return df                                           # Return feature table for the selected element type


def run_anomaly_on_features(df_features: pd.DataFrame,
                            contamination: float = 0.05,
                            save_model_path: Path | None = None) -> pd.DataFrame:
    """
    Runs Isolation Forest anomaly detection on the numeric feature columns
    of the given feature table.

    df_features: DataFrame containing identifiers + numeric features
    returns: DataFrame with anomaly_score and anomaly_label columns appended
    """

    df = df_features.copy()                             # Work on a copy to preserve the original

    # --- 1) Select numeric feature columns automatically ---
    numeric_df = df.select_dtypes(include=["int64", "float64"]).copy()
    # We rely on all numeric columns as input features.
    # Identifiers (GlobalId, PART_POS, etc.) are ignored as they are non-numeric.

    # --- 2) Drop rows with any missing numeric values ---
    numeric_df = numeric_df.apply(pd.to_numeric, errors="coerce")  # Ensure numeric type, coerce invalid to NaN
    mask = numeric_df.notna().all(axis=1)               # True where all numeric features are valid
    X_used = numeric_df.loc[mask].reset_index(drop=True)  # Filtered numeric feature matrix
    df_used = df.loc[mask].reset_index(drop=True)       # Corresponding original rows

    # --- 3) Instantiate IsolationForest model ---
    model = IsolationForest(
        n_estimators=200,                               # Number of trees in the forest
        contamination=contamination,                    # Expected fraction of anomalies
        random_state=42,                                # Reproducibility
    )

    # --- 4) Fit model and compute predictions ---
    model.fit(X_used)                                   # Train model on numeric feature matrix

    labels = model.predict(X_used)                      # +1 = normal, -1 = anomaly
    scores = model.decision_function(X_used)            # Higher = more normal, lower = more anomalous

    # --- 5) Attach anomaly results back to the feature table ---
    df_used["anomaly_score"] = scores                  # Continuous anomaly score
    df_used["anomaly_label"] = labels                  # Discrete label (+1 / -1)

    # --- 6) Optionally save the model ---
    if save_model_path is not None:
        save_model_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure target directory exists
        dump(model, save_model_path)                     # Serialize model to disk

    return df_used                                      # Return feature table with anomaly information


def run_full_pipeline(ifc_path: Path,
                      element_type: str,
                      contamination: float = 0.05,
                      save_model_path: Path | None = None) -> pd.DataFrame:
    """
    Full pipeline for a given IFC file and element type:

    1) Extract element-level features from the IFC (plate / beam / column).
    2) Run unsupervised anomaly detection on those features.
    3) Return a DataFrame containing identifiers, features, and anomaly results.
    """

    df_features = extract_element_features_from_ifc(    # Step 1: feature extraction
        ifc_path=ifc_path,
        element_type=element_type,
    )

    df_result = run_anomaly_on_features(                # Step 2: anomaly detection
        df_features=df_features,
        contamination=contamination,
        save_model_path=save_model_path,
    )

    return df_result                                    # Final result for UI or CSV export


