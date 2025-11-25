import streamlit as st                                                                                                  # Streamlit for the web UI
from pathlib import Path                                            # Elérési utak kezelésére                           # Path library for handling file paths
import tempfile                                                     # Ideiglenes fájlok létrehozására                   # creating temporary files
import sys                                                          # A modul-útvonal módosításához                     # changing module search path

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

from pipeline import run_full_pipeline                                                                                  # the entire pipeline including the functions


# 2. CREATING STATIC WIDGETS
# PAGE and LAYOUT
st.set_page_config(
    layout="wide",
)
# TITLE and DESCRIPTION
st.title("Plate Anomaly Detection")                                                                                     # MAIN TITLE
st.write("Detecting IFC files by bolts and plates.....")                                                                # DESCRIPTION

# 3. SIDEBAR
st.sidebar.header("Settings")                                                                                           # SIDEBAR TITLE
st.logo(
    image="https://fmt.bme.hu/sites/all/themes/epito/images/fmt.bme.hu.png",
    size="large",
    link="https://fmt.bme.hu",
)
# st.logo(
#     image="https://image.pngaaa.com/798/5084798-middle.png",
#     size="large",
#     link="https://docs.streamlit.io/",
# )

# CREATING DYNAMIC WIDGETS
# 3.1 UPLOAD FILE - the user can upload the IFC file
uploaded_file = st.sidebar.file_uploader(
    label="Upload",
    type=["ifc"],
    accept_multiple_files=False,
    help="Upload the IFC file to detect the anomalies.",
    label_visibility="visible",
    width="stretch",
)
# 3.2 SLIDER - the user can set the parameters of the contamination
# It is an assumption that the contamination is the ratio of the most anomalous observations.
contamination = st.sidebar.slider(
    label="Contamination",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01,
    help="The contamination is the ratio of the most anomalous observations. Value 5% is an adequate initial value.",
    label_visibility="visible",
    width="stretch",
)

# 3.3 DROPDOWN LIST - the user can choose what to see in the table
filter_option = st.sidebar.selectbox(
    label="Choose an option what to see",
    options=["All", "Only Anomaly (-1)", "Normal (+1)"],
    index=0,
    help="If you want to see only the anomalies, choose 'Only Anomaly (-1)',choose 'Normal (+1)' for only normal data. 'All' for all data.",
    label_visibility="visible",
    width="stretch",
)

if uploaded_file is None:
    st.sidebar.info("Please upload an ifc or a csv file.")
else:
    st.sidebar.success("File uploaded successfully.")

# 3.4 RUN BUTTON - the user can click the button to run the pipeline
run_button = st.sidebar.button(
    label="Run",
    type="primary",
    help="Click to run the detection.",
    disabled=True if uploaded_file is None else False,
)

# 4. RUN for clicking the button
if run_button: # == True
    # 4.1 temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = Path(tmp_file.name)

    st.write("Temporary ifc file created: ", tmp_file_path)

    # 4.2 THE pipeline
    try:
        running = st.sidebar.text(
            body="It is running..."
        )
        df_result = run_full_pipeline(
            ifc_path=tmp_file_path,
            contamination=contamination,
            save_model_path=None,
        )
        running.text(
            body="Done!"
        )
    except ValueError as e: # missing IfcRelAggregates relation
        st.error(f"{e}")
        st.stop()
    except Exception as e:
        st.error(f"Something went wrong! Error: {type(e).__name__} and {e}")
        st.stop()

    # 4.3 BRIEF SUMMARY STATISTICS
    st.subheader("Summary statistics")

    # Logic
    total_plates = len(df_result)
    total_anomalies = len(df_result[df_result["anomaly_label"] == -1]) # number of rows regarding the dataframe where the condition meets
    anomaly_ratio = total_anomalies / total_plates * 100 if total_plates > 0 else 0

    # Result
    st.write(f"Total number of plates: {total_plates}")
    st.write(f"Total number of anomalies: {total_anomalies}")


    # 4.4 FILTERING
    if filter_option == "All":
        df_result_filtered = df_result
    elif filter_option == "Only Anomaly (-1)":
        df_result_filtered = df_result[df_result["anomaly_label"] == -1]
    elif filter_option == "Normal (+1)":
        df_result_filtered = df_result[df_result["anomaly_label"] == 1]
    else:
        st.error("Invalid filter option selected.")
        pass

    if "anomaly_score" in df_result_filtered.columns:
        df_result_filtered = df_result_filtered.sort_values(
            by="anomaly_score",
            ascending=True  # True, because the lower the score, the more anomalous the plate is
        )
    # 4.5 HIGHLIGHT THE ANOMALIES IN THE TABLE
    def highlight_anomaly(row):
        if row.get("anomaly_label", 1) == -1:
            return ["background-color: #FCC6BB"] * len(row)
        else:
            return [""] * len(row)

    highlighted_df = df_result_filtered.style.apply(
        highlight_anomaly,
        axis=1
    )

    # 4.6 TABLE - to represent the csv -> dataframe and the anomaly columns
    st.subheader("Table of extracted and analyzed data")
    st.dataframe(
        highlighted_df,
        width="stretch"
    )

    # 4.7 EXPORT SETTINGS -> csv
    csv_export_path = Path("../data/result/csv_export.csv")
    csv_export_path.parent.mkdir(parents=True, exist_ok=True)
    df_result_filtered.to_csv(csv_export_path, index=False)

    csv_export = df_result_filtered.to_csv(index=False).encode("utf-8")

    # 4.8 DOWNLOAD BUTTON - to download the csv file
    st.download_button(
        label="Download CSV file",
        data=csv_export,
        file_name=f"{uploaded_file.name}_w_anomalies.csv",
        mime="text/csv",
    )
else: # when run_button == False
    st.info("Please upload an ifc file. If you did, then press the 'Run' button.")
