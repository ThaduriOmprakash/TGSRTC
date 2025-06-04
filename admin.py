import streamlit as st
import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pr@k@sh9347",
        database="DAILY_SCHEDULE_AND_DRIVER_DATA"
    )

def get_all_depots():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM AI", conn)
    conn.close()
    return df

def add_or_update_depot(name, schedules, services, km, depot_category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO AI (depot_name, planned_schedules, planned_services, planned_km, category)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            planned_schedules = VALUES(planned_schedules),
            planned_services = VALUES(planned_services),
            planned_km = VALUES(planned_km),
            category = VALUES(category)
    """, (name, schedules, services, km, category))
    conn.commit()
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Depot Admin Panel")

st.markdown("### ✍️ Add or Update Depot Settings")

depot_name = st.text_input("Depot Name")
category = st.selectbox("Depot Type", ["Select Category","Rural", "Urban"])
planned_schedules = st.number_input("Planned Schedules", min_value=0, step=1)
planned_services = st.number_input("Planned Services", min_value=0, step=1)
planned_km = st.number_input("Planned KM", min_value=0, step=1)


if st.button("Save Depot Settings"):
    if depot_name:
        add_or_update_depot(depot_name, planned_schedules, planned_services, planned_km, category)
        st.success(f"✅ Depot '{depot_name}' settings saved.")
    else:
        st.warning("⚠️ Please enter the depot name.")

st.markdown("### 📋 All Depots")
df = get_all_depots()
st.dataframe(df, use_container_width=True)
