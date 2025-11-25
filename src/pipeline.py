import ifcopenshell
import ifcopenshell.util.element as Element
import pandas as pd
from pathlib import Path

import streamlit
from sklearn.ensemble import IsolationForest
import joblib  # dumps and loads the model
from collections import Counter


# CLASS MAPPING in the UPLOADED IFC
def select_ifc_elements(model: ifcopenshell.file,
                        element_type: str) -> list:
    """
    Selects the given element type from the given IFC model.
    It is a sub-function, which the 'streamlit_ui_app.py' works with via the 'pipeline.py' module

    Parameters
    ----------
    model : ifcopenshell.file object, that the ifcopenshell.open(ifc_path) provides
        this is what the user uploads
    element_type : str
        'plate', 'beam', or 'column'. (in our case it is specified, but can extendable later)

    Returns
    -------
    elements : list
        a list of the different, desired ifc entities like IfcPlate / IfcBeam / IfcColumn / IfcMember
    """

    # 1 Makes the input parameter to lowercase
    e_type = element_type.lower()

    # 2) Element type → IFC osztálylista
    #    Ezek alapján keressük ki az elemeket a modellből
    if e_type == "plate":
        ifc_classes = ["IfcPlate"]
    elif e_type == "beam":
        ifc_classes = ["IfcBeam"]
    elif e_type == "column":
        ifc_classes = ["IfcColumn"]

    # future extension: +"IfcMember"
    # elif e_type == "member/bracing, secondary member, but probably member itself does not work":
    #     ifc_classes = ["IfcMember"]

    # a simple error handling, but the options are going to be in a dropdown list
    else:
        raise ValueError(f"Unsupported element_type: {element_type}")

    # 3) Az összes megfelelő osztály összegyűjtése
    elements = []
    for cls in ifc_classes:
        found = model.by_type(cls)  # Megkeresi a modellben az adott IFC típust
        elements.extend(found)  # Hozzáfűzi a globális listához

    return elements  # A kiválasztott IFC elemek listája


# EXTRACTION to DATAFRAME
def extract_element_features_from_ifc(ifc_path: Path, element_type: str) -> pd.DataFrame:
    """
    Extracts basic identifier-level features for a given element type
    from an IFC model.

    At this stage, only generic metadata is collected:
    - ElementType (plate/beam/column - logical category)
    - IFCClass (e.g., IfcPlate, IfcBeam)
    - GlobalId (unique IFC identifier)
    - Name (IFC name)
    - Tag (often Tekla part mark or internal ID)
    - Numeric geometric / quantity-related values from Tekla property sets
      (e.g., Weight, Length, Width, Height, Perimeter, Areas, Volume).

    Parameters
    ----------
    ifc_path: <- Path
        File system path to the IFC model.
    element_type: <- str
        Logical element type: 'plate', 'beam', or 'column'.

    Returns
    -------
    pd.DataFrame
        A 'df' DataFrame where each row corresponds to a single IFC entity
        of the requested type, with basic identifier information.
    """
    # 1) Open the IFC model from disk
    model = ifcopenshell.open(ifc_path)

    # 2) Select all relevant IFC entities for the requested element type
    elements = select_ifc_elements(model, element_type)

    # 3) If there are no such elements, return an empty DataFrame
    if not elements:
        raise ValueError(f"Element type '{element_type}' not found in this IFC. "
                         f"Probably, this model lacks of it.")

    # 4) Build a list of rows (each row is a Python dict)
    rows = []
    e_type = element_type.lower()

    # Small internal helper: safe conversion to float
    def _to_float_or_none(value):
        """
        Attempts to convert a raw value (string, int, float, etc.) to float.
        Returns None if conversion is not possible.
        """
        if value is None:
            return None
        try:
            # Convert to string first, strip whitespace, then parse as float
            text = str(value).strip()
            if text == "":
                return None
            return float(text.replace(",", "."))  # simple safeguard for comma decimals
        except Exception:
            return None

    for element in elements:
        # --- 4.1 Basic identifiers from the IFC entity itself ---
        guid = getattr(element, "GlobalId", None)  # Robust attribute access
        name = getattr(element, "Name", None)
        tag = getattr(element, "Tag", None)
        ifc_class = element.is_a()  # Actual IFC class name (e.g. "IfcPlate")

        # --- 4.2 Read all property sets for this element ---
        psets = Element.get_psets(element)  # Returns a dict: {pset_name: {prop_name: value, ...}, ...}

        # --- 4.3 UD property sets (if present) ---
        dn_part = psets.get("dn_Part", {})  # Tekla "dn_Part" pset for parts, if exists, but if not then dn_part dict={}

        # From dn_Part: perimeter (mainly relevant for plates, but we keep it general)
        perimeter = dn_part.get("PERIMETER", 0)  # if dn_part exists, then gives keys, if not, then nothing


        # --- 4.4 Tekla Quantity: standard numeric measures provided by Tekla ---
        # These properties are typically available across most Tekla IFC exports.
        # From Tekla Quantity: common numeric measures
        tekla_qty = psets.get("Tekla Quantity", {})  # Tekla quantity / geometry pset
        weight = tekla_qty.get("Weight", None)
        height = tekla_qty.get("Height", None)
        width = tekla_qty.get("Width", None)
        length = tekla_qty.get("Length", None)
        volume = tekla_qty.get("Volume", None)
        # gross_footprint_area = tekla_qty.get("Gross footprint area", None)
        net_surface_area = tekla_qty.get("Net surface area", None)
        area_per_tons = tekla_qty.get("Area per tons", None)


        # --- 4.5 Tekla Common/ CalculatedGeometryValues: elevation and CoG (if available) ---
        # Tekla Common is a frequently used property set that can contain
        # 'Bottom elevation' and 'Top elevation' values as strings.
        # NOTE: Some Tekla exports store elevation and centre-of-gravity information
        # in 'Tekla Common', others may use a custom or calculated set such as
        # 'CalculatedGeometryValues'. We try a small list of candidates.
        # --- 4.5 Tekla Common: elevation-based features (if available) ---
        tekla_common = psets.get("Tekla Common", {})

        phase = tekla_common.get("Phase", None) # if exists, then gives keys, if not, then nothing

        bottom_elev_raw = tekla_common.get("Bottom elevation", None)
        top_elev_raw = tekla_common.get("Top elevation", None)

        bottom_elev = _to_float_or_none(bottom_elev_raw)
        top_elev = _to_float_or_none(top_elev_raw)

        mid_elev = None
        if bottom_elev is not None and top_elev is not None:
            mid_elev = 0.5 * (bottom_elev + top_elev)

        # --- 4.6 CalculatedGeometryValues: center-of-gravity features (if available) ---
        # In the inspected IFC, Trimble Connect shows a property set called
        # 'CalculatedGeometryValues' with fields:
        #   CenterOfGravityX, CenterOfGravityY, CenterOfGravityZ
        # calc_geom = psets.get("CalculatedGeometryValues", {})
        #
        # cogx_raw = calc_geom.get("CenterOfGravityX", None)
        # cogy_raw = calc_geom.get("CenterOfGravityY", None)
        # cogz_raw = calc_geom.get("CenterOfGravityZ", None)
        #
        # cog_x = _to_float_or_none(cogx_raw)
        # cog_y = _to_float_or_none(cogy_raw)
        # cog_z = _to_float_or_none(cogz_raw)

        # --- 4.6 Construct a row dictionary for this element ---
        # Non-numeric identifiers are kept for traceability.
        # Numeric fields may be None here; they will become NaN in the DataFrame
        # and will be handled explicitly before feeding the data to the model.
        # Important note: Key-Value pairs, where the keys can be named !anything! This is what UI is going to show
        row = {
            # Identifier-level metadata
            "ElementType": e_type,
            "IFCClass": ifc_class,
            "GlobalId": guid,
            "Name": name,
            "Tag": tag,

            # dn_Part-based numeric feature(s)
            "Perimeter": perimeter,

            # Tekla Quantity-based numeric features
            "Weight": weight,
            "Height": height,
            "Width": width,
            "Length": length,
            "Volume": volume,
            # "GrossFootprintArea": gross_footprint_area,
            "NetSurfaceArea": net_surface_area,
            "AreaPerTons": area_per_tons,

            # Tekla Common: Elevation-based numeric features
            "Phase": phase,
            "BottomElevation": bottom_elev,
            "TopElevation": top_elev,
            "MidElevation": mid_elev,

            # COG(X,Y,Z)
            # Center of gravity (if available in Tekla Common)
            # "CogX": cog_x,
            # "CogY": cog_y,
            # "CogZ": cog_z,
        }

        rows.append(row)

        # 5) Convert the list of dicts into a DataFrame
    df = pd.DataFrame(rows)

    return df


# FUTURE IMPROVEMENT
# def extract_geometric_features(ifc_file_path):
#     # 1. Geometriai beállítások inicializálása
#     settings = ifcopenshell.geom.settings()
#     settings.set(settings.USE_WORLD_COORDS, True)  # Abszolút (világ) koordináták kellenek!
#
#     model = ifcopenshell.open(ifc_file_path)
#     target_types = ["IfcBeam", "IfcColumn", "IfcPlate"]
#
#     data_rows = []
#
#     for ifc_type in target_types:
#         elements = model.by_type(ifc_type)
#
#         for element in elements:
#             # Ha nincs geometriája (pl. csak logikai elem), ugorjuk át
#             if not element.Representation:
#                 continue
#
#             # --- SÚLYPONT SZÁMÍTÁS ---
#             try:
#                 # Létrehozzuk az alakzatot
#                 shape = ifcopenshell.geom.create_shape(settings, element)
#
#                 # A csúcspontok (vertices) egy lapos listában vannak [x1, y1, z1, x2, y2, z2...]
#                 verts = shape.geometry.verts
#
#                 # Csoportosítjuk 3-asával (x, y, z)
#                 points = np.array(verts).reshape(-1, 3)
#
#                 # Átlagoljuk a pontokat -> ez megadja a geometriai középpontot
#                 # (Ez a befoglaló test közepének felel meg, ML-hez tökéletes)
#                 centroid = points.mean(axis=0)
#
#                 cog_x, cog_y, cog_z = centroid[0], centroid[1], centroid[2]
#
#             except Exception as e:
#                 # Ha nem sikerül a geometria generálás (pl. hibás shape), legyen 0 vagy NaN
#                 # De inkább logolhatjuk is. Itt most átugorjuk a hibás elemet vagy nullázzuk.
#                 cog_x, cog_y, cog_z = 0.0, 0.0, 0.0
#
#             # --- PROPERTIK KINYERÉSE ---
#             psets = ifcopenshell.util.element.get_psets(element)
#
#             # Próbáljuk kinyerni a térfogatot (többféle property set-ből)
#             volume = psets.get("Qto_BeamBaseQuantities", {}).get("NetVolume", 0.0)
#             if volume == 0.0:
#                 volume = psets.get("BaseQuantities", {}).get("NetVolume", 0.0)
#
#             length = psets.get("Dimensions", {}).get("Length", 0.0)
#             area = psets.get("Qto_BeamBaseQuantities", {}).get("NetSurfaceArea", 0.0)
#
#             if volume > 0:
#                 data_rows.append({
#                     "GlobalId": element.GlobalId,
#                     "ElementType": ifc_type,
#                     "Name": element.Name,
#
#                     # Geometriai jellemzők
#                     "Length": length,
#                     "Volume": volume,
#                     "SurfaceArea": area,
#                     "AreaToVolumeRatio": area / volume,
#
#                     # --- ÚJ: KOORDINÁTÁK ---
#                     "COG_X": cog_x,
#                     "COG_Y": cog_y,
#                     "COG_Z": cog_z
#                 })
#
#     return pd.DataFrame(data_rows)

# quick check of output df:

# print(extract_element_features_from_ifc(Path("../data/input/ifc/1051.ifc"), "Beam"))


# PREPARATION for ISOLATION FOREST
def prepare_numeric_features_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects numeric feature columns from the input DataFrame and prepares
    them for consumption by the anomaly detection model.

    Steps:

    1/ Select only columns with numeric dtypes (int64, float64).

    2/ Replace missing values (NaN) with a neutral numeric value (0.0),
    so that the IsolationForest model can operate without errors.

    :parameter:
    ----------
    :param df (pd.DataFrame)
        - Input DataFrame containing identifiers and numeric feature columns.

    :return: numeric_df (pd.DataFrame)
        - A numeric-only DataFrame with no missing values, suitable as input
        to the IsolationForest model.
    """
    # 1) Select numeric columns only and store them in a variable
    numeric_df = df.select_dtypes(include=["int64", "float64"]).copy()

    # 2) Replace all NaN values with 0.0 as a neutral fallback
    #    This ensures that the model does not encounter missing values, does not throw an error, does not distort the scoring
    numeric_df = numeric_df.fillna(0.0)

    return numeric_df


def run_anomaly_detection(df_features: pd.DataFrame,
                          contamination: float = 0.05,
                          save_model_path: Path | None = None) -> pd.DataFrame:
    """
    Runs an IsolationForest-based anomaly detection on the given feature table.

    Steps:

    1/ Prepare a purely numeric feature matrix from the input DataFrame by dropping all non-numeric columns.

    2/ Fit an IsolationForest model on this matrix using the specified contamination ratio.

    3/ Attach the resulting anomaly flags and scores back to the copy of the original DataFrame.

    :parameter:
    -----------

    :param df_features: (pd.DataFrame <- extract_element_features_from_ifc);
        Feature table containing both identifiers and numeric features.
    :param contamination:  (float=0.05, optional, adjustable)
        Expected proportion of anomalies in the dataset, passed directly to the IsolationForest model.
    :param save_model_path: (Path or None, optional, default=None)
        If provided, the trained IsolationForest model will be saved to this file.


    :return:
    df_flagged (pd.DataFrame)
        A copy of the input DataFrame with the two additional columns:
        - AnomalyFlag: discrete label (1 = normal, -1 = anomaly)
        - AnomalyScore: continuous score the higher, the more normal; the lower, the more anomalous
    """

    # 0. avoid errors like value, key, etc.
    if df_features.empty:
        # If the input DataFrame is empty, return a copy of the original DataFrame
        return df_features.copy()
    else:
        pass

    # --- 1) PREPARE NUMERIC-ONLY MATRIX/FEATURES for the ISOLATION FOREST MODEL
    X_numeric = prepare_numeric_features_for_model(df_features)

    # --- 2) GUARD: if there are no numeric columns, we cannot train the model
    if X_numeric.shape[1] == 0:
        raise ValueError("No numeric feature columns available for anomaly detection.")

    # --- 3) Instantiate IsolationForest model ---
    # „model persistence for re-use and reproducibility”
    model = IsolationForest(
        n_estimators=200,  # Number of trees in the forest; more stable, but still fast
        contamination=contamination,  # Expected fraction of anomalies; +UI slider for setting
        random_state=42,  # Reproducibility! to get the same results every time
    )

    # --- 4) Fit model and compute predictions ---
    model.fit(X_numeric)  # Train model on numeric feature matrix

    flags = model.predict(X_numeric)  # +1 = normal, -1 = anomaly
    scores = model.decision_function(X_numeric)  # Higher = more normal, lower = more anomalous

    # --- 5) Attach anomaly results back to the feature table ---
    # Attach results back to a copy of the original feature table
    df_flagged = df_features.copy()
    df_flagged["AnomalyFlag"] = flags  # Discrete label (+1 / -1)
    df_flagged["AnomalyScore"] = scores  # Continuous anomaly score

    # --- 6) Optionally save the model to disk
    if save_model_path is not None:
        save_model_path.parent.mkdir(parents=True, exist_ok=True)  # creates the parent folders too
        joblib.dump(model, save_model_path)

    return df_flagged

def run_full_pipeline(ifc_path: Path,
                      element_type: str,
                      contamination: float = 0.05,
                      save_model_path: Path | None = None) -> pd.DataFrame:

    """
    Runs the complete anomaly-detection pipeline on a single IFC file
    for a given structural element type.

    The pipeline consists of the following stages:

    1/ Extract element-level features from the IFC (plate / beam / column).

    2/ Run unsupervised anomaly detection on those features.

    3/ Return a DataFrame containing identifiers, features, and anomaly results.

    :parameter:
    -----------

    :param ifc_path: Path
        - File system path to the IFC model to be analyzed
    :param element_type: str
        - Logical (engineering) element type to analyze ('plate', 'beam', or 'column')
    :param contamination: float (default=0.05, optional, adjustable)
        - Expected proportion of anomalies in the dataset, passed directly to the IsolationForest model.
    :param save_model_path: Path or None (default=None, optional)
        - If provided, the trained IsolationForest model will be saved to this file.

    :return:
        df_result (pd.Dataframe)
        A DataFrame where each row represents one structural element of the
        requested type, enriched with numeric features as well as:
        - AnomalyFlag: discrete label (1 = normal, -1 = anomaly)
        - AnomalyScore: continuous score the higher, the more normal; the lower, the more anomalous
    """

    # 1. Extract element-level features from the IFC
    df_features = extract_element_features_from_ifc(
        ifc_path,
        element_type
    )

    # 2. GUARD: if there are no features, we cannot run the anomaly detection and stops here
    if isinstance(df_features, pd.DataFrame) and df_features.empty:
        raise ValueError(
            f"No '{element_type}' elements could be extracted from the IFC model. "
            f"The model most likely does not contain this element type."
        )

    # 3. Run anomaly detection on the extracted features
    df_result = run_anomaly_detection(
        df_features,
        contamination,
        save_model_path
    )

    return df_result

# if __name__ == "__main__":
#     test_ifc = Path("../data/input/ifc/1051.ifc")
#     df_beams = run_full_pipeline(
#         ifc_path=test_ifc,
#         element_type="beam",
#         contamination=0.05,
#         save_model_path=None,
#     )
#     print(df_beams.head())
#     print(df_beams[["Weight", "Length", "BottomElevation", "TopElevation", "AnomalyFlag", "AnomalyScore"]].describe())


def scan_ifc(model: ifcopenshell.file):

    # 1) Elem-típusok darabszáma
    types = [element.is_a() for element in model]
    type_counts = Counter(types)

    print(f"{'=== Element type counts (most_common(n=None)) === ':^50}")
    # print(f"{'Type':^40s}| Count")
    for type, count in type_counts.most_common():
        # for type, count in type_counts.items():
        print(f"{type:40s}: {count}")

    print(f"\n{'=== RELATION TYPES IN THIS SPECIFIC IFC FILE ===':^60}")
    for relation_type in ["ifcRelConnectsElements",  # means "is connected to"
                          "ifcRelConnectsWithRealizingElements",  # means "is connected to"
                          "ifcRelAggregates",  # means "is part of"
                          "ifcRelAssociates"]:  # means "is associated with"
        relations = model.by_type(relation_type)
        print(f"{f'Number of {relation_type} relations:':57s} {len(relations)} db")

    return
