import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import sys

# 1 FOLDER STRUCTURE PATHS
# 1.1 Get the path to current script's parent directory, going up one level
current_dir_parent = Path(__file__).parent
print(current_dir_parent)

# 1.2 Get the path to the grand-parent directory of the current script
current_dir_grandparent = current_dir_parent.parent
print(current_dir_grandparent)

sys.path.append(str(current_dir_grandparent))

# it provides the importability of pipeline.py from the same folder and up to 2 levels above
for module in current_dir_grandparent.iterdir():
    if module.is_dir():
        sys.path.append(str(module))

# module for the entry point and backend logic
# this provides the entire pipeline function. Without this, the UI is static and does not allow for dynamic updates
from pipeline import run_full_pipeline


# 2. CREATING STATIC WIDGETS
# PAGE and LAYOUT
st.set_page_config(
    layout="wide",
    page_title="IFC Anomaly Detection with Isolation Forest",
    page_icon=":streamlit:", # https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png
    initial_sidebar_state="expanded",
)
# WEBPAGE-lvl LOGO
st.logo(
    image="https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png",
    size="large",
    link="https://fmt.bme.hu",
)

# 2) PAGE TITLE AND DESCRIPTION
st.title("IFC Anomaly Detection for Structural Elements")
st.write(
    "This application analyses an IFC model and detects potential anomalies "
    "for a selected structural element type (plate, beam, or column) using "
    "an unsupervised IsolationForest model."
)

# 3) SIDEBAR – USER SETTINGS
st.sidebar.header("Settings")
# st.sidebar.title("Settings")
st.sidebar.info("Upload an IFC file, adjust the settings, and press **Run analysis** in the sidebar.")

# 3.1 IFC file upload
uploaded_file = st.sidebar.file_uploader(
    label="Upload IFC file",
    type=["ifc"],
    accept_multiple_files=False,
    help="Upload the IFC model you want to analyse.",
)

if uploaded_file:
    st.sidebar.success("File uploaded successfully.")

# 3.2 Element type selection
element_type = st.sidebar.selectbox(
    label="Element type to analyse",
    options=["Beam", "Column", "Plate"],
    index=0,  # default: "beam"
    help="Choose the logical structural element type you want to analyse."
)

# 3.2 Contamination slider
contamination = st.sidebar.slider(
    label="Contamination (expected anomaly ratio)",
    min_value=0.01,
    max_value=0.20,
    step=0.01,
    value=0.05,
    help=(
        "Expected proportion of anomalies in the dataset. "
        "A value around 5% is a reasonable starting point."
    ),
)

# 3.3 Filter option: what to show in the result table
filter_option = st.sidebar.selectbox(
    label="Filter result table by anomaly flag",
    options=[
        "Show all elements",
        "Only anomalies (AnomalyFlag = -1)",
        "Only normal (AnomalyFlag = 1)",
    ],
    index=0,
    help="Choose content to show in the result table.",
)

# 3.5 Run button
run_button = st.sidebar.button(
    label="Run analysis",
    type="primary",
    help="Button to run the analysis, but it needs an IFC file to work.",
    disabled=True if uploaded_file is None else False,
)

# 4) MAIN LOGIC – ONLY RUN WHEN BUTTON IS PRESSED
if run_button:
    # if uploaded_file is None:
    #     st.error("Please upload an IFC file before running the analysis.")
    #     st.stop()

    # 4.1 Create a temporary file on disk so that pipeline can work with a Path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(uploaded_file.read())
        tmp_ifc_path = Path(tmp.name)

    # st.sidebar.info(f"Temporary IFC file created at: {tmp_ifc_path}")

    # 4.2 Run the full pipeline (feature extraction + anomaly detection)
    try:
        running = st.sidebar.text(
            body="It is running..."
        )
        df_result = run_full_pipeline(
            ifc_path=tmp_ifc_path,
            element_type=element_type,
            contamination=contamination,
            save_model_path=None,  # or Path("../data/models/model.joblib") if you want persistence
        )
        running.success(
            body="Done!"
        )
    except ValueError as ve:
        # Typically raised if the selected element type is not present in the model
        st.error(f"An error occurred during analysis:\n{ve}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error during analysis:\n{e}")
        st.stop()

    # 4.3 Display some key metrics
    total_count = len(df_result)
    anomaly_count = (df_result["AnomalyFlag"] == -1).sum()
    normal_count = (df_result["AnomalyFlag"] == 1).sum()

    st.subheader("Summary statistics")
    st.write(f"Total elements analysed: **{total_count}**")
    st.write(f"Normal elements (AnomalyFlag = 1): **{normal_count}**")
    st.write(f"Anomalous elements (AnomalyFlag = -1): **{anomaly_count}**")

    # 4.4 Apply filtering based on anomaly flag
    df_filtered = df_result.copy()

    if filter_option == "Show all elements":
        df_filtered = df_result
    elif filter_option == "Only anomalies (AnomalyFlag = -1)":
        df_filtered = df_filtered[df_filtered["AnomalyFlag"] == -1]
    elif filter_option == "Only normal elements (AnomalyFlag = 1)":
        df_filtered = df_filtered[df_filtered["AnomalyFlag"] == 1]
    else:
        pass

    if "AnomalyScore" in df_filtered.columns:
        df_filtered = df_filtered.sort_values(
            by="AnomalyScore",
            ascending=True  # True, because the lower the score, the more anomalous the plate is
        )

    # 4.5 HIGHLIGHT THE ANOMALIES IN THE TABLE
    def highlight_anomaly(row):
        if row.get("AnomalyFlag", 1) == -1:
            return ["background-color: #FCC6BB"] * len(row)
        else:
            return [""] * len(row)

    df_highlighted = df_filtered.style.apply(
        highlight_anomaly,
        axis=1
    )

    # 4.6 DISPLAY the FILTERED AND HIGHLIGHTED RESULTS TABLE
    st.subheader("Detailed results")
    st.dataframe(
        df_highlighted,
        width='stretch'
    )

    # 4.6 Export filtered results to CSV
    csv_export_path = Path("../data/result/csv_export.csv")
    csv_export_path.parent.mkdir(parents=True, exist_ok=True)
    df_result.to_csv(csv_export_path, index=False)

    csv_export = df_filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered results as CSV",
        data=csv_export,
        file_name=f"anomaly_results_{element_type}.csv",
        mime="text/csv",
    )

else:
    st.info("Here you will see the results of the analysis.")



