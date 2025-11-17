"""
⭐ LÉPÉS: Minimalista Streamlit UI (a modell eredményeinek megjelenítéséhez)

(Ez lesz a későbbi “Engineer-facing tool” alapja.)

Miért Streamlit?

    1 fájlból működik
    nincs frontend-fejlesztés
    nagyon jól néz ki
    tökéletes diplomamunkához
    könnyen magyarázható a metodológiában

Mit fog tudni az első verzió?

    Betölti a már elkészült predictions_plates.csv-t
    Táblázatban megjeleníti
    Szűrhető lesz az anomáliákra (anomaly_label == -1)
    Letölthető CSV-ben

Ez még NEM futtat új AI modellt, csak vizualizálja az eredményeket.
(Ez a jó irány — később hozzáadjuk az IFC beolvasást is.)
"""

import streamlit
import pandas
from pathlib import Path

# 1 TITLE and HEADER
streamlit.title("Plate Anomaly Detection")
streamlit.write("Detecting by bolt count")

# 2 DATA (csv)
input_path_csv = "data/output/csv_dataframe_flagged/flagged_plates.csv"
dataframe = pandas.read_csv(input_path_csv)

# 3 FILTER
streamlit.header("Filter") # oldalsáv cím
filter_option = streamlit.sidebar.selectbox(
    "What do you want to filter?",
    ("All", "Anomaly", "Normal")
) # dropdown

# 3.1 FILTER LOGIC
if filter_option == "Anomaly":
    filtered_dataframe = dataframe[dataframe["anomaly_label"] == -1] # only anomalies
elif filter_option == "Normal":
    filtered_dataframe = dataframe[dataframe["anomaly_label"] == 1] # normal
else:
    filtered_dataframe = dataframe # All

# 4 TABLE
streamlit.subheader("Result")
streamlit.dataframe(filtered_dataframe, use_container_width=True) # nice automatic table

# 5 DOWNLOADABLE CSV
csv_export = filtered_dataframe.to_csv(index=False).encode("utf-8")
streamlit.download_button(
    label="Download CSV",
    data=csv_export,
    file_name= "filtered_dataframe.csv" if filter_option != "All" else "entire_dataframe.csv",
    mime="text/csv",
)
