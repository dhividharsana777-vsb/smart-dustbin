import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Sample training data
data = {
    "fill_level": [10, 20, 30, 40, 50, 60, 70, 80, 90, 95],
    "temperature": [28, 29, 29, 30, 30, 31, 31, 32, 33, 34],
    "weight": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "status": [
        "Normal", "Normal", "Normal", "Normal", "Normal",
        "Normal", "Warning", "Warning", "Full", "Full"
    ]
}

df = pd.DataFrame(data)

X = df[["fill_level", "temperature", "weight"]]
y = df["status"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "dustbin_model.pkl")

print("Model trained successfully!")