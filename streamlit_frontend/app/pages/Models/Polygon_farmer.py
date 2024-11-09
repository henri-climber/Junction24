from typing import List
class PolygonFarmer:

    #create a class for every single polygon
    def __init__(self, polygon, fetched_data=False, water = None, soil_moisture = None, vegetation_health = None):
        self.polygon = polygon
        self.water = water
        self.fetched_data = fetched_data
        self.soil_moisture = soil_moisture
        self.vegetation_health = vegetation_health
        self.centroid = self.polygon_centroid()
        self.area = self.calculate_area()
        self.color = self.calculate_color()

    def polygon_centroid(self):
        #calculate the centroid of the polygon
        x, y = 0, 0
        coords = self.polygon["geometry"]["coordinates"][0]
        for i in range(len(coords)):
            x += coords[i][0]
            y += coords[i][1]
        x /= len(coords)
        y /= len(coords)
        return x, y

    def calculate_area(self):
        #calculate the area of the polygon
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
        #calculate average of all three values and return color on scale from red to green

        if not self.fetched_data:
            self.color = '#0000FF'
            return self.color


        avg = (self.water + self.soil_moisture + self.vegetation_health) / 3
        #make 10 intervals
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










