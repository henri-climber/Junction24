import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("irrigation_dataset.csv")

# Separate features and target
X = df.drop(columns=["irrigate"])
y = df["irrigate"]

# Convert categorical features to dummy variables for the model
X = pd.get_dummies(X, columns=["vegetation_health", "moisture_index"], drop_first=True)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Initialize and train the decision tree model
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy :", accuracy)

# Save the model
model_path = "irrigation_model.joblib"
joblib.dump(model, model_path)
print(f"Model saved at {model_path}")
