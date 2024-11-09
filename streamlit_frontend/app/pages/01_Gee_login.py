import streamlit as st
import folium
from click import style
from streamlit import columns
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# create state variable for storing drawings
if st.session_state.get('polygons') is None:
    st.session_state.polygons = []

st.set_page_config(layout="wide")
st.title("Draw Your House on the Map")

# Input for address or street name
address = st.text_input("Enter your address or street name:")

if address:
    location = None

    # Geocode the address
    geolocator = Nominatim(user_agent="streamlit_app")
    helper = geolocator.geocode(address)
    if helper:
        location = helper
    else:
        st.write("Address not found. Please enter a valid address.", color = "red")

    if location:
        lat, lon = location.latitude, location.longitude
      #  st.write(f"Coordinates: {lat}, {lon}")
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

        cols = st.columns([0.15, 0.7 , 0.15])
        with cols[1]:
            # Render the map in Streamlit
            map_data = st_folium(m, use_container_width=True, height = 500)

        # Check if a polygon was drawn and extract its coordinates
        if map_data and 'all_drawings' in map_data:
            for p in map_data['all_drawings']:
                st.session_state.polygons.append(PolygonFarmer())
            st.session_state.polygons = map_data['all_drawings']

# Define two columns
left, right = st.columns(2)

# Check if 'drawings' is in session state
if st.session_state.get('polygons'):
    # Display buttons in columns
    left.button(f"🚀 Continue with {len(st.session_state.polygons)} selections.", use_container_width=True, type = "primary")
    right.button("🔁 Select another location", use_container_width=True)