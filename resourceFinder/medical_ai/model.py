import os
import joblib
import string
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

# Function to clean symptoms text
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    return text

# Load the dataset safely
file_path = os.path.join(os.path.dirname(__file__), 'healthcare_data.csv')
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found at path: {file_path}")

data = pd.read_csv(file_path)

# Handle Missing Data (drop if any)
data = data.dropna()

# Step 1: Preprocess Symptoms Text
data['Symptoms'] = data['Symptoms'].apply(clean_text)

# Step 2: Encode Diagnosis
le = LabelEncoder()
data['Diagnosis'] = le.fit_transform(data['Diagnosis'])

# Step 3: Vectorize Symptoms using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))  # Using 1-2 grams for better feature representation
X = vectorizer.fit_transform(data['Symptoms'])
y = data['Diagnosis']

# Step 4: Split Data into Training and Test Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 5: Apply SMOTE for balancing classes in training data
smote = SMOTE(sampling_strategy='auto', random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Step 6: Train the Naive Bayes Model
model = MultinomialNB(alpha=1.0)  # You can adjust alpha here
model.fit(X_train_balanced, y_train_balanced)

# Step 7: Save the model, vectorizer, and label encoder
joblib.dump(model, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump(le, 'label_encoder.pkl')

# Step 8: Evaluate the Model
y_pred = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Function for prediction
def predict_diagnosis(symptoms):
    model = joblib.load('model.pkl')  # Load the trained model
    vectorizer = joblib.load('vectorizer.pkl')  # Load the vectorizer
    label_encoder = joblib.load('label_encoder.pkl')  # Load the label encoder

    symptoms = [clean_text(symptoms)]  # Clean the input symptoms
    symptoms_vector = vectorizer.transform(symptoms)  # Vectorize the cleaned symptoms
    prediction = model.predict(symptoms_vector)
    predicted_diagnosis = label_encoder.inverse_transform(prediction)

    return predicted_diagnosis[0]
