# =============================================
# extract_ifc_data.py
# =============================================
# 7.4.4. Setup of the Isolation Forest Baseline
import sys

import numpy as np
import pandas # dataframe library
from sklearn.ensemble import IsolationForest # machine learning model for anomaly detection
from pathlib import Path # imports the Path class, which is used to handle platform-independent file paths
import joblib # it is for saving the model to file
"""
This script loads a simple placeholder (dummy) dataset containing only one numerical feature column 
and uses the Isolation Forest algorithm to detect anomalies in the data.
This is a placeholder (dummy) model, and should be replaced with a more sophisticated model,
but it is sufficient for demonstration purposes.
Later the model is going to be trained on real-valued features.
For this in-between step the trained model is going to be saved to file 'isolationforest_placeholder.pkl'.
"""
print("*** This is the start. *** \n")
# INPUT: reads the placeholder dataset: features_dummy.csv
input_path = Path("../data/output/csv_dataframe/OF3_parts_Pset01_dataframe.csv")
dataframe = pandas.read_csv(input_path) # 2. reading the file to be a dataframe

# quick check on the dataframe by displaying it, whether we have the expected input
# print(dataframe.head())
# if dataframe["Feature"].all() == 1:
#     print("OK, dataframe is dummy.")
# else:
#     print("This is a real one!")

# the Isolation Forest algorithm
"""
The isolation forest builds an ensemble of decision trees on randomly subsampled
data and uses the ratio of the most anomalous observations as the threshold for
determining outliers. rates the isolation for each sample
"""
# SET UP the model parameters
"""
IsolationForest = fa-alapú, unsupervised anomáliadetektor
A "contamination" paraméter megmondja, anomália-küszöb
Mivel most a placeholder adaton minden "normális", 0.05 (5%) csak tesztérték.
A contamination paraméter az Isolation Forest algoritmusban nem a tanítóadat tényleges hibaarányát írja le, hanem az anomáliákhoz tartozó küszöbérték meghatározásához szükséges technikai beállítás.
Mivel a modell a döntési határ kijelöléséhez legalább minimális anomáliaarányt igényel, a paraméter nem vehet fel nulla értéket.
A jelen kutatásban alkalmazott 0,05-ös (5%) érték csupán módszertani placeholder, amely biztosítja, hogy az algoritmus működő küszöböt állítson be, még akkor is, ha a tanítóadat-halmaz ténylegesen anomáliamentes.
A végleges modell kalibrálásakor ez az érték a valós adatok és azonosított hibák arányához igazítható.
"""
ml_iforest = IsolationForest( # unsupervised learning for anomaly detection
    n_estimators = 100, # "number of trees in the forest", which means the number of random subsets of the training data that are used to train each decision tree
    contamination = 0.05, # necessary for determining the threshold for outliers, which is the ratio of the most anomalous observations, assumption! no expectation
    random_state = 42 # random seed for reproducibility, which is used to initialize the random number generator
)
# print(type(ml_iforest)) # <class 'sklearn.ensemble._iforest.IsolationForest'>
# TRAIN the model
# using random samples (records) the model creates a decision tree to rate the isolation for each sample by counting the splits of tree
# isolate a 'normal' sample -> many branch
# isolate an 'anomaly' sample -> less branch
ml_iforest.fit( # this one carries dataframe_cleaned the actual training process of the 'ml_iforest' model
    dataframe, # X = training data. now it is anomaly-free! -> only dummy training
    y = None, # y = optional target variable, not used in this case
    sample_weight = None # None (default) means each record is treated as an independent, !equally weighted! observation
)

# FLAGGING, "PREDICTION"
# gives a flag for each record # +1 or -1 indicating outlier or not
flags = ml_iforest.predict(dataframe) # Predict if a particular record is an outlier or not
# print(flags.head())
scores = ml_iforest.decision_function(dataframe) # the less the score, the more anomalous # the certainty of the anomaly

# RESULT
# APPEND the flags as 'AnomalyFlag' to the existing dummy dataframe into a new column
flagged_dataframe = dataframe.copy()
flagged_dataframe["AnomalyFlag"] = flags
flagged_dataframe["Scores"] = scores

# OUTPUT csv
output_path = Path("../data/output/csv_dataframe_flagged/flagged_OF3_parts_Pset01_dataframe.csv") # path declaration
output_path.parent.mkdir(parents=True, exist_ok=True) # path creation
# creating a new csv file with the flags
flagged_dataframe.to_csv(output_path, index=False)
# print(dataframe.head())
print(flagged_dataframe.head())

# OUTPUT pkl = the 'whole model itself' including decision trees, hyperparameters, fitted data
model_output_path = Path("../data/output/models/isolationforest_OF3_parts_Pset01.pkl")
model_output_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(value=ml_iforest, filename=model_output_path)
print(f"Trained ML saved to: {model_output_path}")

print("\n *** This is the end. ***")
# =============================================
#   END OF THIS SCRIPT
# =============================================
