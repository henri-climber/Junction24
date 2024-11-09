import joblib
import pandas as pd

from irrigation import fetch_sentinel_data
from weather import check_for_rain, polygon_centroid


def predict(polygon_coords):

    # Load the model
    model = joblib.load("irrigation_model.joblib")

    # fetch the data
    results, _ = fetch_sentinel_data(polygon_coords)
    lon, lat = polygon_centroid(polygon_coords)
    rain_presence = check_for_rain(lat, lon)

    # Evaluating
    if results["Moisture Stress"] > 0.4:
        moisture_index_value = "High"
    elif results["Moisture Stress"] <= 0.4 and results["Moisture Stress"] > 0.2:
        moisture_index_value = "Moderate"
    elif results["Moisture Stress"] <= 0.2 and results["Moisture Stress"] > 0:
        moisture_index_value = "Low"
    else:
        moisture_index_value = "Dry"

    # Prepare the input data for inference
    data = {
        "is_vegetation": [True if results["NDVI Index"] > 0.2 else False],
        "vegetation_health": [
            "Healthy" if results["EVI Index"] > 0.2 else "Not Healthy"
        ],
        "moisture_index": [moisture_index_value],
        "rain_presence": [rain_presence],
    }

    # Convert input data to DataFrame and encode categorical features
    input_df = pd.DataFrame(data)
    input_df = pd.get_dummies(
        input_df, columns=["vegetation_health", "moisture_index"], drop_first=True
    )

    # Ensure input DataFrame has the same columns as training data
    for col in model.feature_names_in_:
        if col not in input_df.columns:
            input_df[col] = 0

    # Predict
    prediction = model.predict(input_df)
    return prediction[0]


if __name__ == "__main__":
    polygon_coords = [
        [16.249166, 52.656369],
        [16.242085, 52.650071],
        [16.260538, 52.643198],
        [16.272211, 52.651242],
        [16.2641, 52.658243],
        [16.249166, 52.656369],
    ]
    print(predict(polygon_coords))
