import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")
st.title("Draw Your House on the Map")

# Input for address or street name
address = st.text_input("Enter your address or street name:")

if address:
    # Geocode the address
    geolocator = Nominatim(user_agent="streamlit_app")
    location = geolocator.geocode(address)

    if location:
        lat, lon = location.latitude, location.longitude
        st.write(f"Coordinates: {lat}, {lon}")

        # Create a folium map centered on the address
        m = folium.Map(location=[lat, lon], zoom_start=18)

        # Add drawing control to the map
        draw = folium.plugins.Draw(
            export=True,
            draw_options={
                "polyline": False,
                "rectangle": False,
                "circle": False,
                "circlemarker": False,
                "polygon": True,
                "marker": False,
            }
        )
        draw.add_to(m)

        # Render the map in Streamlit
        map_data = st_folium(m, width=700, height=500)

        # Check if a polygon was drawn and extract its coordinates
        if map_data and 'all_drawings' in map_data:
            drawings = map_data['all_drawings']
            if drawings:
                # Only capture the first polygon drawn
                first_polygon = drawings[0]
                st.write("Polygon Coordinates:", first_polygon['geometry']['coordinates'])
    else:
        st.write("Address not found. Please enter a valid address.")