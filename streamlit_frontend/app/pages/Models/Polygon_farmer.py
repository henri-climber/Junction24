from shapely.geometry import Polygon

from backend.model.predict import predict_on_polygon


class PolygonFarmer:

    # create a class for every single polygon
    def __init__(self, polygon, fetched_data=False, water=None, soil_moisture=None, vegetation_health=None):
        self.polygon = polygon
        self.water = water
        self.fetched_data = fetched_data
        self.soil_moisture = soil_moisture
        self.vegetation_health = vegetation_health
        self.centroid = self.polygon_centroid()
        self.area = self.calculate_area()
        self.color = self.calculate_color()
        self.temperature = None
        self.humidity = None

    from shapely.geometry import Polygon

    def polygon_centroid(self):
        try:
            # Extract coordinates from the GeoJSON structure
            coords = self.polygon["geometry"]["coordinates"][0]

            # Ensure each point is in (longitude, latitude) format
            coords = [(lon, lat) for lon, lat in coords]

            # Create a Shapely Polygon and calculate its centroid
            polygon = Polygon(coords)

            # Check if the polygon is valid (non-self-intersecting, closed ring, etc.)
            if not polygon.is_valid:
                raise ValueError("Invalid polygon geometry")

            centroid = polygon.centroid

            # Return the centroid's coordinates (longitude, latitude)
            return centroid.x, centroid.y  # x is longitude, y is latitude

        except Exception as e:
            print(f"An error occurred while calculating the centroid: {e}")
            return None, None

    def calculate_area(self):
        # calculate the area of the polygon
        coords = self.polygon["geometry"]["coordinates"][0]
        n = len(coords)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        area = abs(area) / 2
        return area

    def calculate_color(self):
        # calculate average of all three values and return color on scale from red to green

        if not self.fetched_data:
            self.color = '#0000FF'
            return self.color

        avg = (self.water + self.soil_moisture + self.vegetation_health) / 3
        # make 10 intervals
        if avg < 10:
            self.color = '#FF0000'
        elif avg < 20:
            self.color = '#FF3300'
        elif avg < 30:
            self.color = '#FF6600'
        elif avg < 40:
            self.color = '#FF9900'
        elif avg < 50:
            self.color = '#FFCC00'
        elif avg < 60:
            self.color = '#FFFF00'
        elif avg < 70:
            self.color = '#CCFF00'
        elif avg < 80:
            self.color = '#99FF00'
        elif avg < 90:
            self.color = '#66FF00'
        else:
            self.color = '#33FF00'
        return self.color

    def fetch_data(self):
        # fetch data from API
        coords = self.polygon["geometry"]["coordinates"][0]
        print("hjere")
        should_irrigate, evi_index, moisture_stress, current_temp, current_humidity = predict_on_polygon(coords)

        # process predicted data
        self.water = should_irrigate

        # convert the values to percentage

        # moisture stress is in range -1 to 1
        self.soil_moisture = (moisture_stress + 1) * 50

        # evi index is in range 0 to 1
        self.vegetation_health = evi_index * 100

        self.temperature = current_temp
        self.humidity = current_humidity
        self.fetched_data = True
