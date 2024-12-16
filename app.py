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
            "Busan": {"latitude": 35.1796, "longitude": 129.0756},
            "Qingdao": {"latitude": 36.0662, "longitude": 120.3826},
            "Hong Kong": {"latitude": 22.3193, "longitude": 114.1694},
            "Tianjin": {"latitude": 39.1252, "longitude": 117.1994},
            "Rotterdam": {"latitude": 51.9225, "longitude": 4.4792},
            "Jebel Ali": {"latitude": 25.0657, "longitude": 55.1172},
            "Port Klang": {"latitude": 3.0083, "longitude": 101.3923},
            "Xiamen": {"latitude": 24.4798, "longitude": 118.0894},
            "Antwerp": {"latitude": 51.2213, "longitude": 4.4051},
            "Kaohsiung": {"latitude": 22.6273, "longitude": 120.3014},
            "Dalian": {"latitude": 38.9140, "longitude": 121.6147},
            "Los Angeles": {"latitude": 34.0522, "longitude": -118.2437},
            "Hamburg": {"latitude": 53.5511, "longitude": 9.9937},
            "Tanjung Pelepas": {"latitude": 1.3620, "longitude": 103.5376},
            "Laem Chabang": {"latitude": 13.0865, "longitude": 100.8972},
            "Keihin Ports": {"latitude": 35.6590, "longitude": 139.7016},
            "Long Beach": {"latitude": 33.7701, "longitude": -118.1937},
            "Tanjung Priok": {"latitude": -6.1176, "longitude": 106.9083},
            "New York-New Jersey": {"latitude": 40.7128, "longitude": -74.0060},
            "Colombo": {"latitude": 6.9271, "longitude": 79.8612},
            "Ho Chi Minh City": {"latitude": 10.7769, "longitude": 106.7009},
            "Suzhou": {"latitude": 31.2989, "longitude": 120.5853},
            "Piraeus": {"latitude": 37.9475, "longitude": 23.6371},
            "Yingkou": {"latitude": 40.6656, "longitude": 122.2356},
            "Valencia": {"latitude": 39.4699, "longitude": -0.3763},
            "Manila": {"latitude": 14.5995, "longitude": 120.9842},
            "Taicang": {"latitude": 31.4500, "longitude": 121.1000},
            "Hai Phong": {"latitude": 20.8652, "longitude": 106.6839},
            "Algeciras": {"latitude": 36.1408, "longitude": -5.4562},
            "Jawaharlal Nehru Port (Nhava Sheva)": {"latitude": 18.9476, "longitude": 72.9355},
            "Bremen/Bremerhaven": {"latitude": 53.0793, "longitude": 8.8017},
            "Tanger Med": {"latitude": 35.8844, "longitude": -5.4942},
            "Lianyungang": {"latitude": 34.6000, "longitude": 119.1667},
            "Mundra": {"latitude": 22.8396, "longitude": 69.7051},
            "Savannah": {"latitude": 32.0835, "longitude": -81.0998},
            "Tokyo": {"latitude": 35.6828, "longitude": 139.7595},
            "Rizhao": {"latitude": 35.4000, "longitude": 119.5500},
            "Foshan": {"latitude": 23.0215, "longitude": 113.1214},
            "Jeddah": {"latitude": 21.4858, "longitude": 39.1925},
            "Colon": {"latitude": 9.3598, "longitude": -79.9000},
            "Santos": {"latitude": -23.9545, "longitude": -46.3336},
            "Salalah": {"latitude": 17.0197, "longitude": 54.0897},
            "Dongguan": {"latitude": 23.0207, "longitude": 113.7518},
            "Guangxi Beibu": {"latitude": 21.6146, "longitude": 108.3225},
            "Cai Mep": {"latitude": 10.5028, "longitude": 107.0333},
            "Port Said": {"latitude": 31.2653, "longitude": 32.3019},
            "Qinzhou": {"latitude": 21.9500, "longitude": 108.6167},
            "NW Seaport Alliance": {"latitude": 47.6062, "longitude": -122.3321},
            "Felixstowe": {"latitude": 51.9629, "longitude": 1.3511},
            "Marsaxlokk": {"latitude": 35.8410, "longitude": 14.5438},
            "Nanjing": {"latitude": 32.0603, "longitude": 118.7969},
            "Fuzhou": {"latitude": 26.0745, "longitude": 119.2966},
            "Barcelona": {"latitude": 41.3851, "longitude": 2.1734},
            "Vancouver": {"latitude": 49.2827, "longitude": -123.1207},
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
                    "Analyze the following dataset with a focus on the global port performance and its impact on Pelindo Indonesia's competitiveness. "
                    "Provide insights on trade flows, TEUs data, key challenges, and opportunities: \n"
                    + data.to_csv(index=False)
                )

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are an expert data analyst specializing in port and logistics performance."},
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
