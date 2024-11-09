import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Field Monitoring Dashboard",
    layout="wide"
)


# Sample data generation (replace with real data in production)
def generate_sample_data():
    return {
        "vegetation_health": 78,
        "soil_moisture": 45,
        "temperature": 24,
        "humidity": 65,
        "last_rainfall": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "ideal_moisture_min": 40,
        "ideal_moisture_max": 60
    }


def format_metric(value, metric_type):
    """Format the display value for metrics"""
    if metric_type in ['vegetation_health', 'soil_moisture', 'humidity']:
        return f"{value}%"
    elif metric_type == 'temperature':
        return f"{value}°C"
    return str(value)



# Title
st.title("Field Monitoring Dashboard")

# Get data
data = generate_sample_data()

# Create three columns for the main metrics
col1, col2, col3 = st.columns(3)

# Vegetation Health
with col1:
    st.subheader("🌱 Vegetation Health")
    st.metric(
        label="Current Health",
        value=format_metric(data['vegetation_health'], 'vegetation_health')
    )
    if data['vegetation_health'] >= 75:
        st.success("Healthy vegetation")
    elif data['vegetation_health'] >= 50:
        st.warning("Moderate health")
    else:
        st.error("Poor health")

# Soil Moisture
with col2:
    st.subheader("💧 Soil Moisture")
    st.metric(
        label="Current Moisture",
        value=format_metric(data['soil_moisture'], 'soil_moisture')
    )

    # Create a progress bar for soil moisture
    st.progress(data['soil_moisture'] / 100)
    st.caption(f"Ideal range: {data['ideal_moisture_min']}% - {data['ideal_moisture_max']}%")

# Watering Status
with col3:
    st.subheader("⚠️ Watering Status")
    needs_watering = data['soil_moisture'] < data['ideal_moisture_min']
    if needs_watering:
        st.error("Needs Watering!")
    else:
        st.success("Adequate Water")
    st.write(f"Last rainfall: {data['last_rainfall']}")

# Summary section
st.divider()
st.subheader("Field Status Summary")

# Create expander for detailed summary
with st.expander("View Summary", expanded=True):
    # Generate summary text
    status = []
    if data['vegetation_health'] >= 75:
        status.append("healthy vegetation")
    elif data['vegetation_health'] >= 50:
        status.append("moderate vegetation health")
    else:
        status.append("poor vegetation health")

    if needs_watering:
        status.append("needs watering")
    else:
        status.append("adequate moisture")

    summary = f"Field shows {' with '.join(status)}. Last rainfall was on {data['last_rainfall']}."
    st.info(summary)

# Additional metrics
st.divider()
st.subheader("Environmental Conditions")

# Create two columns for additional metrics
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Temperature",
        value=format_metric(data['temperature'], 'temperature'),
        delta="1.2°C"
    )
with col2:
    st.metric(
        label="Humidity",
        value=format_metric(data['humidity'], 'humidity'),
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

# Settings section
st.divider()
st.subheader("Dashboard Settings")

# Create columns for settings
set_col1, set_col2 = st.columns(2)

with set_col1:
    st.number_input("Alert Threshold - Low Moisture (%)",
                    min_value=0, max_value=100,
                    value=data['ideal_moisture_min'])

with set_col2:
    st.number_input("Alert Threshold - High Moisture (%)",
                    min_value=0, max_value=100,
                    value=data['ideal_moisture_max'])

# Add refresh button
if st.button("Refresh Data"):
    st.rerun()