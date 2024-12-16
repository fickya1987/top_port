import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

        # Adding latitude and longitude for specific ports if missing
        coordinates = {
            "Shanghai": {"latitude": 31.2304, "longitude": 121.4737},
            "Singapore": {"latitude": 1.3521, "longitude": 103.8198},
            "Ningbo-Zhoushan": {"latitude": 29.8683, "longitude": 121.5440},
            "Shenzhen": {"latitude": 22.5431, "longitude": 114.0579},
            "Guangzhou Harbor": {"latitude": 23.1291, "longitude": 113.2644},
        }

        if "latitude" not in data.columns or "longitude" not in data.columns:
            data["latitude"] = data["Port Name"].map(lambda x: coordinates.get(x, {}).get("latitude"))
            data["longitude"] = data["Port Name"].map(lambda x: coordinates.get(x, {}).get("longitude"))

        st.write("### Data Preview")
        st.dataframe(data.head())

        # Summary statistics
        st.write("### Summary Statistics")
        st.write(data.describe())

        # Visualisation options
        st.write("### Visualisation")
        columns = data.columns.tolist()
        x_axis = st.selectbox("Select X-axis", columns)
        y_axis = st.selectbox("Select Y-axis", columns)
        chart_type = st.selectbox(
            "Select Chart Type", 
            ["Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot", "Heatmap"]
        )

        if st.button("Generate Plot"):
            fig, ax = plt.subplots()

            if chart_type == "Line Chart":
                ax.plot(data[x_axis], data[y_axis], marker='o')
                ax.set_title(f"{y_axis} vs {x_axis}")
            elif chart_type == "Bar Chart":
                ax.bar(data[x_axis], data[y_axis])
                ax.set_title(f"{y_axis} vs {x_axis}")
            elif chart_type == "Scatter Plot":
                ax.scatter(data[x_axis], data[y_axis])
                ax.set_title(f"{y_axis} vs {x_axis}")
            elif chart_type == "Histogram":
                ax.hist(data[y_axis], bins=20)
                ax.set_title(f"Histogram of {y_axis}")
            elif chart_type == "Box Plot":
                sns.boxplot(x=data[x_axis], y=data[y_axis], ax=ax)
                ax.set_title(f"Box Plot of {y_axis} by {x_axis}")
            elif chart_type == "Heatmap":
                if data.select_dtypes(include=["number"]).shape[1] > 1:
                    sns.heatmap(data.corr(), annot=True, cmap="coolwarm", ax=ax)
                    ax.set_title("Correlation Heatmap")
                else:
                    st.error("Heatmap requires at least two numerical columns.")

            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            st.pyplot(fig)

        # Geomap Visualisation
        st.write("### Geomap Visualisation")
        if "latitude" in data.columns and "longitude" in data.columns:
            map_center = [data["latitude"].mean(), data["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=5)

            for _, row in data.iterrows():
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=f"Port: {row['Port Name']}<br>Country: {row['Country']}<br>TEUs: {row['MillionTEU2023']}M",
                ).add_to(m)

            st.write("#### Geomap")
            st_folium(m, width=700, height=500)
        else:
            st.info("No 'latitude' and 'longitude' columns found in the dataset for geomap visualisation.")

        # AI Analysis
        st.write("### AI Data Analysis")
        if st.button("Generate AI Analysis"):
            try:
                prompt = (
                    "Analyze the following dataset and provide key insights: \n"
                    + data.head(10).to_csv(index=False)
                )

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a data analyst."},
                              {"role": "user", "content": prompt}]
                )
                st.write("#### AI Analysis Result:")
                st.write(response['choices'][0]['message']['content'])

            except Exception as e:
                st.error(f"Error generating analysis: {e}")

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("Please upload a file to proceed.")
