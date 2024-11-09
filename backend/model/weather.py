import os
from dotenv import load_dotenv
import requests
import datetime
import math

load_dotenv()

API_KEY = os.getenv("OPEN_WEATHER_API")


def polygon_centroid(polygon_coords):
    """
    Calculate the centroid (geometric center) of a polygon given its coordinates.

    Parameters:
    polygon_coords (list of lists): A list of [longitude, latitude] pairs representing the vertices of the polygon.

    Returns:
    tuple: The (longitude, latitude) of the centroid.
    """
    n = len(polygon_coords)
    if n == 0:
        raise ValueError("The polygon must have at least one vertex.")

    # Initialize sums
    sum_x = 0
    sum_y = 0
    sum_area = 0

    # Iterate over each vertex and calculate the centroid
    for i in range(n):
        x0, y0 = polygon_coords[i]
        x1, y1 = polygon_coords[(i + 1) % n]
        cross_product = x0 * y1 - x1 * y0
        sum_x += (x0 + x1) * cross_product
        sum_y += (y0 + y1) * cross_product
        sum_area += cross_product

    # Calculate the area of the polygon
    area = 0.5 * sum_area

    if area == 0:
        raise ValueError("The polygon has zero area.")

    # Calculate the centroid
    centroid_x = sum_x / (6 * area)
    centroid_y = sum_y / (6 * area)

    return centroid_x, centroid_y


# Function to get current weather data by coordinates
def get_current_weather(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data


# Function to get forecasted weather data by coordinates
def get_forecast_weather(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data


# Main function to check for rain
def check_for_rain(api_key, lat, lon):
    current_weather = get_current_weather(api_key, lat, lon)
    forecast_weather = get_forecast_weather(api_key, lat, lon)

    # Extract relevant data from current weather
    current_precipitation = current_weather.get("rain", {}).get(
        "1h", 0
    )  # Rain in the last hour

    # Extract relevant data from forecast weather
    forecast_list = forecast_weather["list"]
    forecasted_precipitation = 0
    for forecast in forecast_list:
        forecast_time = datetime.datetime.fromtimestamp(forecast["dt"])
        if forecast_time <= datetime.datetime.now() + datetime.timedelta(days=3):
            forecasted_precipitation += forecast.get("rain", {}).get("3h", 0)

    # Determine irrigation need
    if current_precipitation > 5 or forecasted_precipitation > 10:
        return True
    else:
        return False


if __name__ == "__main__":
    polygon_coords = [
        [16.249166, 52.656369],
        [16.242085, 52.650071],
        [16.260538, 52.643198],
        [16.272211, 52.651242],
        [16.2641, 52.658243],
        [16.249166, 52.656369],
    ]
    lon, lat = polygon_centroid(polygon_coords)
    print(check_for_rain(API_KEY, lat, lon))
