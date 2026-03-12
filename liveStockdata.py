import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Configuration ---
st.set_page_config(page_title="LiveStock Monitor", layout="wide")

# --- 2. Authentication Logic ---
def check_password():
    """Returns True if the user had the correct password."""
    def login_form():
        with st.form("Login"):
            st.subheader("🔒 Admin Login")
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if user == "admin" and pw == "admin":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

    if "authenticated" not in st.session_state:
        login_form()
        return False
    return True

# --- 3. Database Connection ---
def get_data():
    try:
        conn = mysql.connector.connect(
            host="82.180.143.66",
            user="u263681140_students",
            password="testStudents@123",
            database="u263681140_students"
        )
        # Added latitude and longitude to the query
        query = "SELECT id, DateTime, temp, humi, heartRate, Oxygen, latitude, longitude FROM LiveStock"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return pd.DataFrame()

# --- 4. Main App Logic ---
if check_password():
    # --- Auto Refresh (10 Seconds) ---
    st_autorefresh(interval=10 * 1000, key="data_refresh")

    # Sidebar Logout
    with st.sidebar:
        st.title("Settings")
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()
        st.info("Refreshing every 10 seconds")

    st.title("🚜 LiveStock Real-Time Sensor Dashboard")

    df = get_data()

    if not df.empty:
        # Data Processing
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        sensor_cols = ['temp', 'humi', 'heartRate', 'Oxygen']
        
        for col in sensor_cols + ['latitude', 'longitude']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- Tabs for different views ---
        tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📍 GPS Tracking", "📄 Raw Data"])

        with tab1:
            st.subheader("📈 Multi-Sensor Time Series Analysis")
            
            df_melted = df.melt(
                id_vars=['DateTime'], 
                value_vars=sensor_cols, 
                var_name='Sensor_Type', 
                value_name='Value'
            )

            fig = px.line(
                df_melted, 
                x='DateTime', 
                y='Value', 
                color='Sensor_Type',
                markers=True,
                title="Live Sensor Readings Over Time",
                template="plotly_dark"
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("📍 Real-Time Location")
            # Filter rows with valid GPS data
            gps_df = df.dropna(subset=['latitude', 'longitude'])
            
            if not gps_df.empty:
                # Rename columns for st.map compatibility (needs 'lat' and 'lon')
                map_df = gps_df[['latitude', 'longitude']].rename(
                    columns={'latitude': 'lat', 'longitude': 'lon'}
                )
                st.map(map_df)
                
                # Show latest coordinates
                latest = gps_df.iloc[-1]
                st.write(f"**Last Known Position:** {latest['latitude']}, {latest['longitude']} (Recorded: {latest['DateTime']})")
            else:
                st.warning("No GPS coordinates available in database.")

        with tab3:
            st.subheader("Database Export")
            st.dataframe(df.sort_values(by='DateTime', ascending=False), use_container_width=True)

    else:
        st.warning("No data found. Check your database connection.")
