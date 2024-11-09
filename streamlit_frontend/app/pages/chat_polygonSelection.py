import streamlit as st
from typing import List
import folium
import os
from click import style
from streamlit import columns, session_state
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

from app.pages.Models.Polygon_farmer import PolygonFarmer
from app.pages.chat_result import select_and_display_details_for_polygon


def create_areas_to_monitor(location: str):
    if "show_select_polygon_page" not in st.session_state:
        st.session_state.show_select_polygon_page = False

    # set location state to the location
    st.session_state.location = location

    def style2(selected):
        return {
            'fillColor': 'blue',
            'color': 'blue',
            'weight': 0.5
        }

    # create state variable for storing drawings if not already created
    if st.session_state.get('polygons') is None:
        st.session_state.polygons: List[PolygonFarmer] = []

    # create state variable for storing drawings
    if st.session_state.get('location'):
        # get lat, lon from location
        geolocator = Nominatim(user_agent="streamlit_app")
        location = geolocator.geocode(st.session_state.location)
        lat, lon = location.latitude, location.longitude

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
                "polygon": not st.session_state.show_select_polygon_page,
                "marker": False,
            }
        )
        draw.add_to(m)

        for p in st.session_state.polygons:
            folium.GeoJson(p.polygon, name="Polygon", style_function=style2).add_to(m)

        # Render the map in Streamlit
        map_data = st_folium(m, use_container_width=True, height=500)

        # Check if a polygon was drawn and extract its coordinates
        if map_data and 'all_drawings' in map_data and map_data['all_drawings']:
            for p in map_data['all_drawings']:
                st.session_state.polygons.append(PolygonFarmer(p))
            st.rerun()  # Refresh the map after drawing a polygon

        # Add a submit button
        if not st.session_state.show_select_polygon_page:
            if st.button("Submit"):
                st.session_state.show_select_polygon_page = True

    else:
        st.write("Address not found. Please enter a valid address.", color="red")

    if st.session_state.show_select_polygon_page:
        select_and_display_details_for_polygon()


create_areas_to_monitor("Munich")
