import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# --- 1. Database Connection Configuration ---
def get_data():
    try:
        conn = mysql.connector.connect(
            host="82.180.143.66",
            user="u263681140_students",
            password="testStudents@123",
            database="u263681140_students"
        )
        # Selecting specific columns as requested (excluding latitude/longitude)
        query = "SELECT id, DateTime, temp, humi, heartRate, Oxygen FROM LiveStock"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return pd.DataFrame()

# --- 2. Page Setup ---
st.set_page_config(page_title="LiveStock Monitor", layout="wide")
st.title("🚜 LiveStock Real-Time Sensor Dashboard")

# --- 3. Data Processing ---
df = get_data()

if not df.empty:
    # Convert DateTime column to actual datetime objects
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    
    # Convert VARCHAR sensor columns to Float for graphing
    sensor_cols = ['temp', 'humi', 'heartRate', 'Oxygen']
    for col in sensor_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where all sensor data is missing to keep the graph clean
    df = df.dropna(subset=sensor_cols, how='all')

    # --- 4. Display Data Table ---
    with st.expander("📄 View Raw Data Table", expanded=True):
        st.dataframe(df.sort_values(by='DateTime', ascending=False), use_container_width=True)

    # --- 5. Graphical Visualization ---
    st.subheader("📈 Multi-Sensor Time Series Analysis")
    
    # "Melting" the data: This transforms columns into rows so Plotly can 
    # color-code them easily in one single graph.
    df_melted = df.melt(
        id_vars=['DateTime'], 
        value_vars=sensor_cols, 
        var_name='Sensor_Type', 
        value_name='Value'
    )

    # Creating the Interactive Line Graph
    fig = px.line(
        df_melted, 
        x='DateTime', 
        y='Value', 
        color='Sensor_Type',
        markers=True,
        title="Live Sensor Readings Over Time",
        template="plotly_dark"  # Professional dark theme
    )

    # Customizing axes
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Time of Recording",
        yaxis_title="Reading Value",
        legend_title="Sensors"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data found in the 'LiveStock' table. Check your database connection or table content.")
