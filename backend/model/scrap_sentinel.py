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


def get_data(polygon_coords, time_interval, resolution, evalscript):
    """
    Download Sentinel-2 data for a given area of interest, time interval, resolution, and EvalScript.

    Parameters:
    - polygon_coords (list): Coordinates defining the area of interest as a polygon.
    - time_interval (tuple): Date range as a tuple (start_date, end_date) in "YYYY-MM-DD" format.
    - resolution (int): Spatial resolution in meters.
    - config: SentinelHub configuration instance.
    - evalscript (str): Custom EvalScript for processing Sentinel-2 data.

    Returns:
    - image (array): Downloaded image data.
    """
    # Define bounding box and size
    bbox = BBox(bbox=polygon_to_bbox(polygon_coords), crs=CRS.WGS84)
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
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=size,
        config=config,
    )

    # Download and save the data
    image = request.get_data(save_data=True)[0]
    return image


if __name__ == "__main__":
    evalscript = """
        // A simple Evalscript example that fetches the true color image
        // True color uses RGB bands
        return [B04, B03, B02];
    """
    time_interval = ("2022-01-01", "2022-01-10")
    resolution = 10
    polygon_coords = [
        [16.249166, 52.656369],
        [16.242085, 52.650071],
        [16.260538, 52.643198],
        [16.272211, 52.651242],
        [16.2641, 52.658243],
        [16.249166, 52.656369],
    ]
    image = get_data(polygon_coords, time_interval, resolution, config, evalscript)
    print(image)
