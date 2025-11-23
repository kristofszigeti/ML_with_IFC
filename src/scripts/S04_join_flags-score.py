"""
Visszacsatolás a GlobalId-hoz

Cél: a modell-eredményt (score, label) összekapcsolni az eredeti CSV soraival GlobalId alapján, de úgy, hogy a GlobalId nem megy be a modellbe.

Mit csinálunk?

    1. Beolvassuk az eredeti (166×3) CSV-t → ebből csak a GlobalId kell.
    2. Beolvassuk a model kimenetet (predictions.csv → jelenleg Feature, anomaly_score, anomaly_label).
    3. Sorazonos összefűzés (index alapján), majd GlobalId hozzáadása.

    Mentés: data/processed/predictions_with_ids.csv.
"""

import pandas
from pathlib import Path

# FILES
# we need the dataframe with GUID
input_raw_csv_filename = "OF3_parts_Pset01"

# we need the dataframe with flags and scores
input_csv_flagged_df_filename = "flagged_OF3_parts_Pset01_dataframe"


# PATHS
# it contains the GUID
raw_path = Path(f"../data/input/csv/{input_raw_csv_filename}.csv")

# numeric dataframe with flags and scores
flagged_path = Path(f"../data/output/csv_dataframe_flagged/{input_csv_flagged_df_filename}.csv")

# combined dataframes
relinked_path = Path("../../data/output/relinked/joined_data_OF3.csv")
relinked_path.parent.mkdir(parents=True, exist_ok=True)


raw_dataframe = pandas.read_csv(raw_path, usecols=["GUID"]) # fetches the GUID column we link to
print(raw_dataframe.head())
flagged = pandas.read_csv(flagged_path) # fetches all columns we link

joined = pandas.concat([raw_dataframe.reset_index(drop=True), flagged.reset_index(drop=True)], axis=1)
# A reset_index(drop=True) újraszámozza a DataFrame sorait, és eldobja a régi indexet, így biztosítva, hogy concat vagy maszkos szűrés után a sorok ismét tisztán, egymást követően legyenek számozva.
# Ez garantálja az 1:1 párosítást a másik DataFrame-fel való összeillesztésnél.
print(joined.head())
joined.to_csv(relinked_path, index=False)

print(f"New content in {relinked_path}")

