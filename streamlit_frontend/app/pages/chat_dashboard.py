import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.pages.Models.Polygon_farmer import PolygonFarmer


def polygon_details_page(polygon: PolygonFarmer):
    def format_metric(value, metric_type):
        """Format the display value for metrics"""
        if metric_type in ['vegetation_health', 'soil_moisture', 'humidity']:
            # round to 1 decimal place and add a percentage sign
            return f"{value:.1f}%"
        elif metric_type == 'temperature':
            return f"{value:.2f}°C"
        return str(value)

    # Title
    st.title(f"Showing Details for Selected Polygon {polygon.pid}")

    # Create three columns for the main metrics
    col1, col2, col3 = st.columns(3)

    # Vegetation Health
    with col1:
        st.subheader("🌱 Vegetation Health")
        st.metric(
            label="Current Health",
            value=format_metric(polygon.vegetation_health, 'vegetation_health')
        )
        if polygon.vegetation_health >= 20:
            st.success("Healthy")
        elif polygon.vegetation_health >= 10:
            st.warning("Moderate health")
        else:
            st.error("Poor health")

    # Soil Moisture
    with col2:
        st.subheader("💧 Soil Moisture")
        st.write("")
        st.metric(
            label="Current Moisture",
            value=format_metric(polygon.soil_moisture, 'soil_moisture')
        )

        # Create a progress bar for soil moisture
        st.progress(polygon.soil_moisture / 100)
        st.caption(f"Ideal range: 40% - 60%")

    # Watering Status
    with col3:
        st.subheader("⚠️ Watering Recommendation")
        needs_watering = polygon.water
        if needs_watering:
            st.error("Needs Watering!")
        else:
            st.success("Adequate Water")

    # Summary section
    st.divider()
    st.subheader("Field Status Summary")

    # Create expander for detailed summary
    with st.expander("View Summary", expanded=True):
        # Generate summary text
        status = []
        if polygon.vegetation_health >= 20:
            status.append("healthy vegetation")
        elif polygon.vegetation_health >= 10:
            status.append("moderate vegetation health")
        else:
            status.append("poor vegetation health")

        if needs_watering:
            status.append("needs watering")
        else:
            status.append("adequate moisture")

        summary = f"Field shows {' with '.join(status)}."
        st.info(summary)

    # Additional metrics
    st.divider()
    st.subheader("Environmental Conditions")

    # Create two columns for additional metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Temperature",
            value=format_metric(polygon.temperature, 'temperature'),
            delta="1.2°C"
        )
    with col2:
        st.metric(
            label="Humidity",
            value=format_metric(polygon.humidity, 'humidity'),
            delta="-2%"
        )

    # Historical Data
    st.divider()
    st.subheader("Historical Data")

    # Tab layout for different historical views
    tab1, tab2 = st.tabs(["7 Days", "30 Days"])

    # Generate sample historical data
    def get_historical_data(days):
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        return pd.DataFrame({
            'Date': dates,
            'Vegetation Health': np.random.uniform(70, 85, days),
            'Soil Moisture': np.random.uniform(40, 60, days),
            'Temperature': np.random.uniform(20, 28, days)
        })

    with tab1:
        hist_data_7 = get_historical_data(7)
        st.line_chart(hist_data_7.set_index('Date'))

    with tab2:
        hist_data_30 = get_historical_data(30)
        st.line_chart(hist_data_30.set_index('Date'))
