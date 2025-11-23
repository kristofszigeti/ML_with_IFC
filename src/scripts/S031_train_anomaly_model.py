"""
Oké, akkor most ráengedjük az IsolationForest-et a valódi bolt_count feature-re, és visszacsatoljuk az eredményt a Plate-ekhez.

Most egy új scriptet csinálunk, ami ÖNMAGÁBAN elintézi:

beolvasás: plate_features.csv

numerikus feature képzés: bolt_count

modell tanítás: IsolationForest

eredmények visszaírása Plate-szinten: predictions_plates.csv

Nem fogunk most a features.csv-re támaszkodni, hogy ne legyen elcsúszás a szűrések miatt.

🚩 Script: src/train_plate_anomaly.py
Feladata röviden

plate_features.csv → kivesszük belőle a bolt_count-ot

kiszűrjük a rossz sorokat (NaN, nem szám)

IsolationForest-et tanítunk

visszaírjuk az eredményeket:
"""

import pandas as pd                           # Táblázatos adatokhoz
from pathlib import Path                      # Elérési utak kezeléséhez
from sklearn.ensemble import IsolationForest  # Anomáliadetektáló modell
from joblib import dump                       # Modell mentéséhez .pkl formában

# 1) Bemeneti és kimeneti útvonalak
in_path = Path("../../data/output/csv_dataframe/plate_features.csv")          # Plate + bolt_count adat
out_path = Path("../../data/output/csv_dataframe_flagged/flagged_plates.csv")     # Ide mentjük az eredményeket
model_path = Path("../../data/models/isoforest_boltcount.pkl")     # Ide mentjük a tanult modellt

# 2) Kimeneti mappák biztosítása
out_path.parent.mkdir(parents=True, exist_ok=True)   # processed mappa létrehozása, ha nincs
model_path.parent.mkdir(parents=True, exist_ok=True) # models mappa létrehozása, ha nincs

# 3) Plate-feature tábla beolvasása
df = pd.read_csv(in_path)       # PlateGlobalId, Assembly..., bolt_count oszlopokkal

# 4) Numerikus feature (bolt_count) kivétele
X = df[["bolt_count"]].copy()   # Csak a bolt_count oszlopot használjuk bemenetként

# 5) Biztosítjuk, hogy bolt_count numerikus legyen
X["bolt_count"] = pd.to_numeric(X["bolt_count"], errors="coerce")  # Hibás értékek → NaN

# 6) NaN értékek kiszűrése
mask = X["bolt_count"].notna()          # True ott, ahol érvényes a bolt_count
X_used = X.loc[mask].reset_index(drop=True)   # Csak a használható sorok a modellnek
df_used = df.loc[mask].reset_index(drop=True) # Ugyanezek a plate sorok metaadatokkal

# 7) Rövid riport a tanítóadatról (dokumentációhoz jól jön)
print("Összes plate sor        :", len(df))
print("Felhasznált plate sorok :", len(df_used))
print("bolt_count statisztika a tanítóhalmazon:")
print(X_used["bolt_count"].describe())

# 8) IsolationForest modell példányosítása
model = IsolationForest(
    n_estimators=200,     # Fák száma az erdőben (stabilitás)
    contamination=0.05,   # Becslés: kb. 5% anomália várható
    random_state=42,      # Reprodukálhatóság (ugyanaz az eredmény futásról futásra)
)

# 9) Modell tanítása a bolt_count adatra
model.fit(X_used)   # A modell megtanulja, mi számít "normális" boltszámnak

# 10) Anomália címkék és pontszámok számítása
labels = model.predict(X_used)            # +1 = normál, -1 = anomália
scores = model.decision_function(X_used)  # Minél kisebb, annál inkább anomália

# 11) Eredmények visszacsatolása a plate metaadatokhoz
df_used["anomaly_score"] = scores        # Folytonos anomália-pontszám
df_used["anomaly_label"] = labels        # Diszkrét címke: +1 / -1

# 12) Eredmények mentése CSV-be
df_used.to_csv(out_path, index=False)    # Minden plate sor + boltszám + anomália eredmény

# 13) Modell mentése .pkl fájlba (későbbi UI / újrafuttatás miatt)
dump(model, model_path)

print(f"\n✅ Predictions saved to: {out_path}")
print(f"✅ Model saved to: {model_path}")
print("\nMinta eredmények:")
print(df_used.head())
