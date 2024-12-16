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
st.title("Data Visualisation and Analytics with AI")

# File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)

        # Search Engine Feature
        st.write("### Search Port or Country")
        search_query = st.text_input("Search for a port or country:")
        if search_query:
            filtered_data = data[data.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
            st.write("#### Search Results:")
            st.dataframe(filtered_data)

        # Geomap Visualisation
        st.write("### Geomap Visualisation")
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
            st.info("No 'latitude' and 'longitude' columns found in the dataset for geomap visualisation.")

        # Interactive Visualisation with Plotly
        st.write("### Interactive Visualisation")
        columns = data.columns.tolist()
        x_axis = st.selectbox("Select X-axis", columns)
        y_axis = st.selectbox("Select Y-axis", columns)
        chart_type = st.selectbox(
            "Select Chart Type", 
            ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram"]
        )

        if st.button("Generate Interactive Plot"):
            if chart_type == "Line Chart":
                fig = px.line(data, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Bar Chart":
                fig = px.bar(data, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Scatter Plot":
                fig = px.scatter(data, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Histogram":
                fig = px.histogram(data, x=x_axis, title=f"Histogram of {x_axis}")

            st.plotly_chart(fig)

        # AI Analysis Options
        st.write("### AI Data Analysis")
        analysis_type = st.radio("Pilih jenis analisis:", ["Analisis Berdasarkan Data", "Pencarian Detail GPT-4o"])
        analysis_query = st.text_area("Deskripsi analisis atau detail pencarian:")
        if st.button("Generate AI Analysis") and analysis_query:
            try:
                if analysis_type == "Analisis Berdasarkan Data":
                    prompt = (
                        f"Berdasarkan dataset berikut, lakukan analisis mendalam tentang '{analysis_query}'. Fokuskan analisis pada kinerja pelabuhan, tren TEUs, dan peluang untuk Pelindo Indonesia:\n"
                        + data.to_csv(index=False)
                    )
                else:
                    prompt = (
                        f"Cari informasi lengkap tentang '{analysis_query}' yang relevan dengan performa pelabuhan dunia. Tambahkan referensi sumber terpercaya."
                    )

                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    temperature=1,
                    max_completion_tokens=2048,
                    messages=[{"role": "system", "content": "Anda adalah analis data berpengalaman."},
                              {"role": "user", "content": prompt}]
                )
                result = response['choices'][0]['message']['content']
                st.write("#### Hasil Analisis AI:")
                st.write(result)

            except Exception as e:
                st.error(f"Error generating analysis: {e}")

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("Please upload a file to proceed.")



