import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import sys

def main():
    try:
        # STEP 3: LOAD DATA
        print("--- Loading Dataset (Units: KM and KM/HR) ---")
        df = pd.read_csv('warehouse_data.csv')
        print(f"First 5 rows:\n{df.head()}\n")
        print("Dataset info:")
        print(df.info())
        print("-" * 30)

        # STEP 4: CREATE TARGET VARIABLE
        # Define logic for risk levels (using km)
        def get_risk_level(dist_km):
            if dist_km < 2.0:
                return "collision"
            elif 2.0 <= dist_km <= 5.0:
                return "warning"
            else:
                return "safe"

        df['risk_level'] = df['distance_km'].apply(get_risk_level)
        print("Target variable 'risk_level' created based on KM thresholds.")

        # STEP 5: FEATURE SELECTION
        X = df[['distance_km', 'speed_kmhr', 'object_detected']]
        y = df['risk_level']
        print(f"Features: {list(X.columns)}")
        print(f"Target: risk_level")

        # STEP 6: ENCODE DATA
        label_mapping = {"collision": 0, "warning": 1, "safe": 2}
        reverse_mapping = {v: k for k, v in label_mapping.items()}
        y_encoded = y.map(label_mapping)

        # STEP 7: TRAIN-TEST SPLIT (80/20)
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        print(f"Split completed. Train size: {len(X_train)}, Test size: {len(X_test)}")

        # STEP 8: TRAIN MODEL
        print("--- Training Decision Tree Classifier ---")
        model = DecisionTreeClassifier(random_state=42)
        model.fit(X_train, y_train)

        # STEP 9: EVALUATE MODEL
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy * 100:.2f}%")

        print("\nPredictions vs Actual (Sample 5 rows):")
        results_df = pd.DataFrame({
            'Actual': [reverse_mapping[val] for val in y_test[:5]],
            'Predicted': [reverse_mapping[val] for val in y_pred[:5]]
        })
        print(results_df)
        print("-" * 30)

        # STEP 10: USER INPUT PREDICTION
        print("\n--- Real-Time Collision Risk Prediction ---")
        try:
            user_dist = float(input("Enter distance (km): "))
            user_speed = float(input("Enter speed (km/hr): "))
            # Assume sensor trigger based on the simulation logic (dist < 5km)
            user_obj = 1 if user_dist < 5.0 else 0

            # Predict
            user_features = pd.DataFrame([[user_dist, user_speed, user_obj]], 
                                       columns=['distance_km', 'speed_kmhr', 'object_detected'])
            prediction_encoded = model.predict(user_features)[0]
            prediction_label = reverse_mapping[prediction_encoded]

            # STEP 11: OUTPUT
            print("\n" + "="*40)
            print("PREDICTION RESULT")
            print("="*40)
            print(f"Distance: {user_dist} km | Speed: {user_speed} km/hr")
            print(f"RISK LEVEL: {prediction_label.upper()}")
            print("="*40)
            
        except ValueError:
            print("Invalid input! Please enter numeric values.")

    except FileNotFoundError:
        print("Error: warehouse_data.csv not found. Please run generate_data.py first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()