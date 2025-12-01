# ================================== #
# UI: STREAMLIT                      #
# ================================== #
# IMPORT (initial libraries)
import streamlit as st
from pathlib import Path
import tempfile
import sys

# 1 FOLDER STRUCTURE PATHS
# Initialize the path and folder-levels where the pipeline.py (or any module) is located
# 1.1 Get the path to the current script's parent directory, going up one level
current_dir_parent = Path(__file__).parent
# print(current_dir_parent)

# 1.2 Get the path to the grandparent directory of the current script
current_dir_grandparent = current_dir_parent.parent
# print(current_dir_grandparent)

sys.path.append(str(current_dir_grandparent))

# it provides the importability of pipeline.py (or whatever my module is) from the same level of folders and up to 2 levels upwards
# there is no search downwards
for module in current_dir_grandparent.iterdir():
    if module.is_dir():
        sys.path.append(str(module))

# IMPORT WORKFLOW (pipeline.py)
# module for the entry point and backend logic
# this provides the entire pipeline function. Without this, the UI is static and does not allow for dynamic updates
from pipeline import run_full_pipeline

# IMPORT VISUALIZATION (visualization.py)
try:
    from visualization import plot_anomaly_visualization # so it tries to import the visualization module
except ImportError:
    # Fallback for when the visualization module is not available via the given path.
    # But the sys.path is supposed to protect the flow up to 2 levels and sidewards
    pass

# 2. CREATING STATIC WIDGETS
# PAGE and LAYOUT
st.set_page_config(
    layout="wide",
    page_title="IFC Anomaly Detection with Isolation Forest",
    page_icon=":streamlit:", # https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png
    initial_sidebar_state="expanded",
)
# WEBPAGE-Body-lvl LOGO
# UI LAYOUT: 3 columns for logos
col1, col2, col3, col4, col5 = st.columns(
    spec=5,
    gap="small",
    width=325
)
# LOGOS
logo_fmt = "https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png"
logo_streamlit = "https://images.seeklogo.com/logo-png/44/1/streamlit-logo-png_seeklogo-441815.png"
logo_python = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkdgUkYVq9-UPHtkrQyNzA1t-hCdSG65-XYw&s"
logo_aut = "https://avatars.githubusercontent.com/u/12133481?s=280&v=4"
logo_buildingsmart = "https://www.buildingsmart.org/wp-content/uploads/2024/07/buildingSMART-International-favicon-color.png"

with col1:
    st.image(
        image=logo_fmt,
        width=150
    )
with col2:
    st.image(
        image=logo_aut,
        width=400
    )
with col3:
    st.image(
        image=logo_streamlit,
        width=150
    )
with col4:
    st.image(
        image=logo_python,
        width=150
    )
with col5:
    st.image(
        image=logo_buildingsmart,
    )

# WEBPAGE-lvl LOGO
# st.logo(
#     image="https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png",
#     size="large",
#     link="https://fmt.bme.hu",
# )

# 2) PAGE TITLE AND DESCRIPTION
st.title("IFC Anomaly Detection for Structural Elements with Machine Learning Isolation Forest")
st.markdown(
    body="This application analyses an IFC model and detects potential anomalies or draw the attention to possible outliers, "
    "for a selected structural element type (plate, beam, or column) using "
    "an unsupervised IsolationForest model.",
    width=1200
)

# 3) SIDEBAR – USER SETTINGS
st.sidebar.header("Settings")
# st.sidebar.title("Settings")
st.sidebar.info("Follow the steps below!")

# WIDGETS for USER INPUT
# 3.1 IFC file upload
uploaded_file = st.sidebar.file_uploader(
    label="I. Upload IFC file you would like to analyse",
    type=["ifc"],
    accept_multiple_files=False,
    help="The file must be in IFC format (.ifc) and embodies a steel structure for correct analysis.",
)

if uploaded_file:
    st.sidebar.success("File uploaded successfully.")

st.sidebar.divider()

# 3.2 Element type selection
element_type = st.sidebar.selectbox(
    label="II. Choose an element type to analyse",
    options=["---", "Beam", "Column", "Plate"],
    index=0,  # default: "beam"
    help="Choose the logical structural element type you want to analyse."
)
if element_type != "---":
    st.sidebar.success(f"{element_type} are chosen to be analysed.")

st.sidebar.divider()

# 3.2 Contamination slider
contamination = st.sidebar.slider(
    label="III. Set the Contamination value (expected anomaly ratio)",
    min_value=0.01,
    max_value=0.20,
    step=0.01,
    value=0.05,
    help=(
        "Expected proportion of anomalies in the dataset."
        "A value around 5% is a reasonable starting point."
    ),
)


# 3.5 Run button
run_button = st.sidebar.button(
    label="Run analysis",
    type="primary",
    help="Button to run the analysis, but it needs an IFC file to work.",
    disabled=True if uploaded_file is None else False,
)

# 4) MAIN LOGIC – ONLY RUN WHEN BUTTON IS PRESSED
if run_button and uploaded_file is not None:
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

        st.session_state["df_result"] = df_result
        st.session_state["data_loaded"] = True

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

if "df_result" in st.session_state and st.session_state["data_loaded"]:
    df_result = st.session_state["df_result"]

    # 4.3 Display some key metrics
    total_count = len(df_result)
    anomaly_count = (df_result["AnomalyFlag"] == -1).sum()
    normal_count = (df_result["AnomalyFlag"] == 1).sum()

    st.subheader("Summary statistics")
    st.write(f"Total elements analysed: **{total_count}**")
    st.write(f"Normal elements (AnomalyFlag = 1): **{normal_count}**")
    st.write(f"Anomalous elements (AnomalyFlag = -1): **{anomaly_count}**")

    # VISUALIZATION of the UPLOADED IFC FILE
    st.markdown(
        body="---", # SECTION SEPARATOR
        width='stretch'
    ) # practically just a simple line for separation
    st.subheader("Visualization")

    # fetch only the relevant numerical columns for the visualization
    numerical_columns = df_result.select_dtypes(include=["int64", "float64"]).columns.tolist()
    # drop out the anomaly flag column because the score is descriptive enough
    plot_columns = [column for column in numerical_columns if column not in ["AnomalyFlag"]]

    # UI LAYOUT: 2 columns for drop-down
    col1, col2 = st.columns(2)

    with col1:
        # Alapértelmezett X tengely: Próbáljunk okosat tippelni (pl. Length vagy Weight)
        default_x = "AnomalyScore" #if "Length" in plot_columns else plot_columns[0]
        x_axis = st.selectbox(
            label="Select X axis for Scatter Plot",
            options=plot_columns,
            index=plot_columns.index(default_x) if default_x in plot_columns else 0)

    with col2:
        # Alapértelmezett Y tengely: Próbáljunk okosat tippelni (pl. Weight vagy Volume)
        default_y = "Weight" if "Weight" in plot_columns else (plot_columns[1] if len(plot_columns) > 1 else plot_columns[0])
        y_axis = st.selectbox(
            label="Select Y axis for Scatter Plot",
            options=plot_columns,
            index=plot_columns.index(default_y) if default_y in plot_columns else 0)

    # Grafikon generálása és megjelenítése
    if not df_result.empty:
        fig = plot_anomaly_visualization(df_result, x_axis, y_axis)
        st.pyplot(fig)
    else:
        st.warning("Not enough data to create visualization.")

    st.markdown("---") # SECTION SEPARATOR

    # 4.4 Apply filtering based on anomaly flag
    df_filtered = df_result.copy()

    # 3.3 Filter option: what to show in the result table
    filter_option = st.selectbox(
        label=" IV. Filter the result table by anomaly flag",
        options=[
            "Show all elements",
            "Only anomalies (AnomalyFlag = -1)",
            "Only normal (AnomalyFlag = 1)",
        ],
        index=0,
        help="Choose content to show in the result table. You can see the anomalies highlighted.",
        width=300,
    )
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
            return ["background-color: #EE948B"] * len(row) # a bit lighter: #F2A49B
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
    st.info(
        body=(
            "Hi! Here you will see the results of the analysis.\n\n"
            "The current version offers two charts and a result table.\n\n"
            "But first, check the sidebar!"
        ),
        width='stretch'
    )



