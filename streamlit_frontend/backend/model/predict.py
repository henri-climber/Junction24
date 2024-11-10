import joblib
import pandas as pd
import os

from backend.model.irrigation import fetch_sentinel_data
from backend.model.weather import check_for_rain, polygon_centroid


def predict_on_polygon(polygon_coords):
    """
    Predict whether to irrigate based on the Sentinel-2 and weather data.
    :param polygon_coords: List of coordinates of the polygon
    :return:
    Prediction - Whether to irrigate or not
    EVI Index - healthy if > 0.2,
    Moisture Stress -  -1 < dry < 0 < low < 0.2 < moderate < 0.4 < high
    Current Temperature - Temperature at the centroid of the polygon
    Current Humidity - Humidity at the centroid of the polygon
    """
    # Load the model
    cwd = os.getcwd()
    model = joblib.load(f"{cwd}/backend/model/irrigation_model.joblib")

    # fetch the data
    results, images = fetch_sentinel_data(polygon_coords)
    print(images)
    lon, lat = polygon_centroid(polygon_coords)
    rain_presence, current_temp, current_humidity = check_for_rain(lat, lon)

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
    return prediction[0], results["EVI Index"], results["Moisture Stress"], current_temp, current_humidity


if __name__ == "__main__":
    polygon_coords = [
        [16.249166, 52.656369],
        [16.242085, 52.650071],
        [16.260538, 52.643198],
        [16.272211, 52.651242],
        [16.2641, 52.658243],
        [16.249166, 52.656369],
    ]
    print(predict_on_polygon(polygon_coords))
