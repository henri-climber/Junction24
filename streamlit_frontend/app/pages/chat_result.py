import streamlit as st
import folium
from typing import List
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from shapely.geometry import Point, Polygon
from typing import Optional
from app.pages.Models.Polygon_farmer import PolygonFarmer


def style1(selected):
    return {
        'fillColor': 'red',
        'color': 'red',
        'weight': 2
    }
def style2(selected):
    return {
        'fillColor': 'blue',
        'color': 'blue',
        'weight': 0.5
    }


# Ensure session state stores the polygons
if "polygons" not in st.session_state:
    st.session_state.polygons = []
if "selected_polygon" not in st.session_state:
    st.session_state.selected_polygon: Optional[PolygonFarmer] = None


# write function that calculate avg coordinates of all polygons
def avg_coords(polygons: List[PolygonFarmer]):
    if not polygons:
        return None

    sum_lat = 0
    sum_lon = 0
    for p in polygons:
        coords = p.polygon['geometry']['coordinates'][0][0]
        sum_lat += coords[1]
        sum_lon += coords[0]

    avg_lat = sum_lat / len(polygons)
    avg_lon = sum_lon / len(polygons)
    return avg_lat, avg_lon

#calc middle
middle = None
if "polygons" in st.session_state:
    middle = avg_coords(st.session_state.polygons)

if middle:
    st.set_page_config(layout="wide")
    st.title("Review Your Selected Area")

    lat, lon = middle
    # Create a folium map centered on the address
    m = folium.Map(location=[lat, lon], zoom_start=18)

    # Add previously drawn polygons to the map
    for p in st.session_state.polygons:
        if p == st.session_state.selected_polygon:
            folium.GeoJson(p.polygon, name="Polygon", style_function=style1).add_to(m)
        else:
            folium.GeoJson(p.polygon, name="Polygon", style_function=style2).add_to(m)

    # Center and add marker on the selected polygon if exists
    if st.session_state.selected_polygon:
        coords = st.session_state.selected_polygon.polygon['geometry']['coordinates'][0]
        centroid_lat = sum(point[1] for point in coords) / len(coords)
        centroid_lon = sum(point[0] for point in coords) / len(coords)
        folium.Marker([centroid_lat, centroid_lon], icon=folium.Icon(color="red"), popup="Selected Polygon").add_to(m)
        m.location = [centroid_lat, centroid_lon]
        m.zoom_start = 18

    cols = st.columns([0.15, 0.7 , 0.15])
    with cols[1]:
        # Render the map in Streamlit
        map_data = st_folium(m, use_container_width=True, height=500)

    # Handle polygon selection
    if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
        last_clicked = map_data['last_clicked']
        click_point = Point(last_clicked['lng'], last_clicked['lat'])

        for polygon_farmer in st.session_state.polygons:
            # Convert the polygon's coordinates to a Shapely Polygon
            polygon_coords = polygon_farmer.polygon['geometry']['coordinates'][0]
            polygon_shapely = Polygon(polygon_coords)

            # Check if the clicked point is inside the polygon
            if polygon_shapely.contains(click_point):
                if polygon_farmer == st.session_state.selected_polygon:
                    st.session_state.selected_polygon = None
                else:
                    st.session_state.selected_polygon = polygon_farmer
                st.rerun()
                

# Display selected polygon details below the map
if st.session_state.selected_polygon:
    st.write("### Selected Polygon Details")
    # Additional information can be added here


