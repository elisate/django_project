import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load dataset
data = pd.read_csv("medical_ai/ai_model/dataset.csv")

# Prepare data
X = data.drop(columns=["disease"])
y = data["disease"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Save Model
joblib.dump(model, "medical_ai/ai_model/model.pkl")
print("Model trained and saved!")
