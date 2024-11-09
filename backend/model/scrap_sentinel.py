import os
from dotenv import load_dotenv
from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    bbox_to_dimensions,
)

load_dotenv()

# Configure API credentials
config = SHConfig()
config.instance_id = os.getenv("INSTANCE_ID")
config.sh_client_id = os.getenv("CLIENT_ID")
config.sh_client_secret = os.getenv("CLIENT_SECRET")

polygon_coords = [
    [16.249166, 52.656369],
    [16.242085, 52.650071],
    [16.260538, 52.643198],
    [16.272211, 52.651242],
    [16.2641, 52.658243],
    [16.249166, 52.656369],
]


# Define a function to convert a polygon to a bounding box
# To do: account for multipolygons
def polygon_to_bbox(polygon_coords):
    # Extract all longitudes and latitudes from the polygon points
    longitudes = [point[0] for point in polygon_coords]
    latitudes = [point[1] for point in polygon_coords]

    # Get the min and max for both longitude and latitude
    min_lon = min(longitudes)
    max_lon = max(longitudes)
    min_lat = min(latitudes)
    max_lat = max(latitudes)

    # Return the bounding box in the format [min_lon, min_lat, max_lon, max_lat]
    return [min_lon, min_lat, max_lon, max_lat]


def calculate_dynamic_resolution(bbox):
    min_lon, min_lat, max_lon, max_lat = bbox
    lon_diff = max_lon - min_lon
    lat_diff = max_lat - min_lat

    # Set base resolution factor based on typical values for Sentinel-2
    # Increase the resolution (decrease resolution value) for smaller areas
    area = lon_diff * lat_diff  # Approximate area in degrees²
    if area > 0.05:
        resolution = 20  # Low resolution for large areas
    elif area > 0.01:
        resolution = 10  # Medium resolution
    else:
        resolution = 5  # High resolution for small areas

    return resolution


def get_data(polygon_coords, time_interval, evalscript):
    """
    Download Sentinel-2 data for a given area of interest, time interval, and EvalScript.

    Parameters:
    - polygon_coords (list): Coordinates defining the area of interest as a polygon.
    - time_interval (tuple): Date range as a tuple (start_date, end_date) in "YYYY-MM-DD" format.
    - config: SentinelHub configuration instance.
    - evalscript (str): Custom EvalScript for processing Sentinel-2 data.

    Returns:
    - image (array): Downloaded image data.
    """
    # Define bounding box and size
    bbox_coords = polygon_to_bbox(polygon_coords)
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    resolution = calculate_dynamic_resolution(bbox_coords)
    size = bbox_to_dimensions(bbox, resolution=resolution)

    # Define the request for Sentinel-2 data
    request = SentinelHubRequest(
        data_folder="output",
        evalscript=evalscript,  # Use the passed EvalScript
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.PNG),
            SentinelHubRequest.output_response("index", MimeType.TIFF),
        ],
        bbox=bbox,
        size=size,
        config=config,
    )

    # Download and save the data
    image = request.get_data()[0]

    return image


if __name__ == "__main__":
    evalscript = """
        // A simple Evalscript example that fetches the true color image
        // True color uses RGB bands
        return [B04, B03, B02];
    """
    time_interval = ("2022-01-01", "2022-01-10")
    polygon_coords = [
        [16.249166, 52.656369],
        [16.242085, 52.650071],
        [16.260538, 52.643198],
        [16.272211, 52.651242],
        [16.2641, 52.658243],
        [16.249166, 52.656369],
    ]
    image = get_data(polygon_coords, time_interval, evalscript)
    print(image)
