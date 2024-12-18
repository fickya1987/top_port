import streamlit as st
import pandas as pd
import plotly.express as px
import openai
from dotenv import load_dotenv
import os
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit App
st.title("Pelindo AI Business Analytics")

# File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)

        # Ensure TEU column is numeric
        if 'MillionTEU2023' in data.columns:
            data['MillionTEU2023'] = pd.to_numeric(data['MillionTEU2023'], errors='coerce')
        else:
            st.error("No column named 'MillionTEU2023' found in dataset.")

        # Display raw table
        st.write("### Uploaded Data Table")
        st.dataframe(data)

        # Geomap Visualization
        st.write("### Geomap Visualization")
        if "latitude" in data.columns and "longitude" in data.columns:
            map_center = [data["latitude"].mean(), data["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=2)

            for _, row in data.iterrows():
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=f"<b>Port:</b> {row['Port Name']}<br><b>Country:</b> {row['Country']}<br><b>TEUs:</b> {row['MillionTEU2023']}M",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)

            st.write("#### Geomap")
            st_folium(m, width=800, height=500)
        else:
            st.info("No 'latitude' and 'longitude' columns found in the dataset for geomap visualization.")

        # Interactive Visualization
        st.write("### TEU Bar Chart")
        if "Port Name" in data.columns and "MillionTEU2023" in data.columns:
            fig = px.bar(data, x="Port Name", y="MillionTEU2023", title="TEU Volume by Port Name")
            st.plotly_chart(fig)
        else:
            st.error("Required columns 'Port Name' or 'MillionTEU2023' not found in the dataset.")

        # Search Engine Feature
        st.write("### Search Port or Country")
        search_query = st.text_input("Search for a port or country:")
        if search_query:
            filtered_data = data[data.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
            st.write("#### Search Results:")
            st.dataframe(filtered_data)

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a file to proceed.")

