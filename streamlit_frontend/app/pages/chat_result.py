import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from shapely.geometry import Point, Polygon



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

# Ensure session state stores the drawings
if "drawings" not in st.session_state:
    st.session_state.drawings = []
if "selected_polygon" not in st.session_state:
    st.session_state.selected_polygon = None


# write function that calculate avg coordinates of all drawings
def avg_coords(drawings):
    if not drawings:
        return None

    sum_lat = 0
    sum_lon = 0
    for drawing in drawings:
        coords = drawing['geometry']['coordinates'][0][0]
        sum_lat += coords[1]
        sum_lon += coords[0]

    avg_lat = sum_lat / len(drawings)
    avg_lon = sum_lon / len(drawings)
    return avg_lat, avg_lon

#calc middle
middle = None
if "drawings" in st.session_state:
    middle = avg_coords(st.session_state.drawings)

if middle:
    st.set_page_config(layout="wide")
    st.title("Review Your Selected Area")

    lat, lon = middle
    # Create a folium map centered on the address
    m = folium.Map(location=[lat, lon], zoom_start=18)

    # Add previously drawn polygons to the map
    for drawing in st.session_state.drawings:
        if drawing == st.session_state.selected_polygon:
            folium.GeoJson(drawing, name="Polygon", style_function=style1).add_to(m)
        else:
            folium.GeoJson(drawing, name="Polygon", style_function=style2).add_to(m)

    # Center and add marker on the selected polygon if exists
    if st.session_state.selected_polygon:
        coords = st.session_state.selected_polygon['geometry']['coordinates'][0]
        centroid_lat = sum(point[1] for point in coords) / len(coords)
        centroid_lon = sum(point[0] for point in coords) / len(coords)
        folium.Marker([centroid_lat, centroid_lon], popup="Selected Polygon").add_to(m)
        m.location = [centroid_lat, centroid_lon]
        m.zoom_start = 18

    # Add drawing control to allow selecting another area
    draw = folium.plugins.Draw(
        export=True,
        draw_options={
            "polyline": False,
            "rectangle": False,
            "circle": False,
            "circlemarker": False,
            "polygon": False,
            "marker": False,
        }
    )
    draw.add_to(m)

    cols = st.columns([0.15, 0.7 , 0.15])
    with cols[1]:
        # Render the map in Streamlit
        map_data = st_folium(m, use_container_width=True, height=500)

    # Handle polygon selection
    if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
        last_clicked = map_data['last_clicked']
        click_point = Point(last_clicked['lng'], last_clicked['lat'])

        for drawing in st.session_state.drawings:
            # Convert the drawing's coordinates to a Shapely Polygon
            polygon_coords = drawing['geometry']['coordinates'][0]
            polygon = Polygon(polygon_coords)

            # Check if the clicked point is inside the polygon
            if polygon.contains(click_point):
                st.session_state.selected_polygon = drawing
                map_data.update()
                break

# Display selected polygon details below the map
if st.session_state.selected_polygon:
    st.write("### Selected Polygon Details")
    st.write(f"Coordinates: {st.session_state.selected_polygon['geometry']['coordinates']}")
    # Additional information can be added here

