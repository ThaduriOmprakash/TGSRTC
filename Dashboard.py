import streamlit as st
import mysql.connector
from datetime import date
import pandas as pd
import altair as alt

st.set_page_config(page_title="TGSRTC Productivity Dashboard", layout="wide")

st.title("TGSRTC PRODUCTIVITY DASHBOARD")

# Sidebar dropdown menu
menu = [
    "Daily Depot Input Sheet",
    "Productivity Budget 8 Ratios (Rural/Urban)",
    "Productivity Budget vs. Actual 8 Ratios",
    "Depot Dashboard",
    "AI Depot Tool",
    "Driver Dashboard"
]

selection = st.sidebar.selectbox("Select Screen", menu)

# Content display based on selection
if selection == "Daily Depot Input Sheet":
    st.header("DAILY SCHEDULE AND DRIVER DATA")
    
  # Hide the number input steppers (arrows)
    hide_streamlit_style = """
    <style>
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none;
        margin: 0; 
    }
    input[type=number] {
        -moz-appearance: textfield;
    }
    </style>
    """
   
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)



    # MySQL connection
    def get_connection():
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="Pr@k@sh9347",
                database="DAILY_SCHEDULE_AND_DRIVER_DATA"
            )
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
            return None

    # Fetch depot settings from MySQL
    def get_depot_settings():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM AI")
        rows = cursor.fetchall()
        conn.close()
        return {row["depot_name"]: row for row in rows}

    # Insert daily record into MySQL
    def insert_data(data):
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO day_records (
                depot_name, entry_date, planned_schedules, planned_services, planned_km,
                actual_services, actual_km, service_variance, km_variance,
                total_drivers, medically_unfit, suspended_drivers,
                available_drivers_1, percent_available_drivers_1, weekly_off, special_off,
                other, long_leave, sick_leave_S, long_absent_A, leave_L, available_drivers_2,
                percent_available_drivers_2, spot_absent, attending_drivers, percent_attending_drivers,
                drivers_required, driver_schedule, driver_shortage, double_duty, off_cancellation,
                drivers_on_duty, drivers_as_conductors, drivers_for_bus_services, km_per_driver,
                service_driver_check, spondilitis, spinal_disc, vision_color_blindness, m_neuro,
                m_paralysis, m_total_drivers, m_diff, flu_fever, bp, orthopedic_problem,
                heart_problem, weakness, eye_problem, accident_injuries, s_neuro, piles, diabetes,
                thyroid, gas_problem, dental, ear, s_paralysis, general_surgery,
                s_total_drivers, s_diff, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, data)
        conn.commit()
        conn.close()


    # App setup
    #st.set_page_config(page_title="Depot Daily Tracker", layout="centered")
    #st.markdown("### 🚚 DAILY SCHEDULE AND DRIVER DATA")
    st.markdown("### 📝 Enter New Record")



    # Load depot settings
    depot_config = get_depot_settings()
    depot_list = sorted(depot_config.keys())

    with st.form("entry_form"):
        st.subheader("SCHEDULES")
        col34,col35=st.columns(2)
        with col34:
            depot_name = st.selectbox("Select Depot", depot_list)
        with col35:
            entry_date = st.date_input("Select Date", value=date.today())

        if depot_name in depot_config:
            settings = depot_config[depot_name]
            planned_schedules = settings.get("planned_schedules", 0)
            planned_services = settings.get("planned_services", 0)
            planned_km = settings.get("planned_km", 0)
        else:
            planned_schedules = planned_services = planned_km = 0

        st.markdown("### 🔒 Predefined Depot Values")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Planned Schedules", planned_schedules)
        col2.metric("Planned Services", planned_services)
        col3.metric("Planned KM (0)", planned_km)
        
        
        
        col22,col23 = st.columns(2)
        with col22:
            actual_services = st.number_input("Actual Services", min_value=0)
        with col23:
            actual_km = st.number_input("Actual KM", min_value=0, step=1)

        service_variance = actual_services - planned_services
        km_variance = actual_km - planned_km

        col4, col5 = st.columns(2)
        col4.metric("Service Variance", service_variance)
        col5.metric("KM Variance", km_variance)

        st.markdown("### 👥 Driver Availability")
        
        col24,col25,col26 = st.columns(3)
        with col24:
            total_drivers = st.number_input("Total Drivers", min_value=0, step=1)
        with col25:
            medically_unfit = st.number_input("Medically Unfit", min_value=0, step=1)
        with col26:
            suspended_drivers = st.number_input("Suspended Drivers", min_value=0, step=1)

        available_drivers_1 = total_drivers - medically_unfit - suspended_drivers
        percent_available_drivers_1 = (available_drivers_1 / total_drivers * 100) if total_drivers else 0.0

        col6, col7 = st.columns(2)
        col6.metric("Available Drivers-1", available_drivers_1)
        col7.metric("% Available Drivers-1", f"{percent_available_drivers_1:.2f}%")

        # Additional Leave Inputs
        col27,col28,col29,col30,col31,col32,col33 =st.columns(7)
        with col27:
             weekly_off = st.number_input("Weekly Off", min_value=0, step=1)
        with col28:
            special_off = st.number_input("Special Off", min_value=0, step=1)
        with col29:
             other = st.number_input("Others", min_value=0, step=1)
        with col30:
            long_leave = st.number_input("Long Leave", min_value=0, step=1)
        with col31:
            sick_leave_S = st.number_input("Sick Leave (S)", min_value=0, step=1)
        with col32:
            long_absent_A = st.number_input("Long Absent (A)", min_value=0, step=1)
        with col33:
            leave_L = st.number_input("Leave (L)", min_value=0, step=1)
        available_drivers_2 = available_drivers_1 - (weekly_off + special_off + other + long_leave + sick_leave_S + long_absent_A + leave_L)
        percent_available_drivers_2 = (available_drivers_2 / total_drivers * 100) if total_drivers else 0.0
        col8, col9 = st.columns(2)
        col8.metric("Available Drivers-2", available_drivers_2)
        col9.metric("% Available Drivers-2", f"{percent_available_drivers_2:.2f}%")

        spot_absent = st.number_input("Spot Absent", min_value=0, step=1)
        attending_drivers = available_drivers_2 - spot_absent
        percent_attending_drivers = (attending_drivers / total_drivers * 100) if total_drivers else 0.0

        col10, col11 = st.columns(2)
        col10.metric("Attending Drivers", attending_drivers)
        col11.metric("% Attending", f"{percent_attending_drivers:.2f}%")

        # More inputs for final calculations
        drivers_required = st.number_input("Drivers Required", min_value=0, step=1)
        driver_schedule = (drivers_required / planned_schedules) if planned_schedules else 0.0
        driver_shortage = 0
        if drivers_required > attending_drivers:
            driver_shortage = drivers_required - attending_drivers 
        
        col12, col13 = st.columns(2)
        col12.metric("Driver schedule",driver_schedule)
        col13.metric("Driver shortage",driver_shortage)
        
        col57,col58 =st.columns(2)
        with col57:
            double_duty = st.number_input("Double Duty", min_value=0, step=1)
        with col58:
            off_cancellation = st.number_input("Off Cancellation", min_value=0, step=1)
        
        drivers_on_duty = attending_drivers + double_duty + off_cancellation
        col14a,col14b =st.columns(2)
        col14a.metric("Drivers on Duty",drivers_on_duty)
        
        drivers_as_conductors = st.number_input("Drivers as Conductors", min_value=0, step=1)
        drivers_for_bus_services = drivers_on_duty - drivers_as_conductors
        km_per_driver = (actual_km / drivers_for_bus_services) if drivers_for_bus_services else 0.0
        service_driver_check = drivers_for_bus_services - actual_services
        col15,col16,col17=st.columns(3)
        col15.metric("Driver for Bus Services",drivers_for_bus_services)
        col16.metric("KM/Driver",km_per_driver)
        col17.metric("Service/Driver Check",service_driver_check)
        
        
        st.markdown("### Medically Unfit Reasons")
        col36,col37,col38,col39,col40 =st.columns(5)
        with col36:
            spondilitis = st.number_input("Spondilitis", min_value=0, step=1)
        with col37:
            spinal_disc = st.number_input("Spinal Disc", min_value=0, step=1)
        with col38:
            vision_color_blindness = st.number_input("Vision/Color Blindness", min_value=0, step=1)
        with col39:
            m_neuro = st.number_input("Neuro", min_value=0, step=1)
        with col40:
            m_paralysis = st.number_input("Paralysis", min_value=0, step=1)
        m_total_drivers = spondilitis + spinal_disc +  vision_color_blindness +  m_neuro + m_paralysis
        m_diff = m_total_drivers - medically_unfit
        col18,col19=st.columns(2)
        col18.metric("Total Drivers",m_total_drivers)
        col19.metric("Diff",m_diff)
        
        if m_diff != 0 :
            st.error("Diff value should be equals to 0")
        
        
        st.markdown("### Sick Reasons")
        col41,col42,col43,col44 = st.columns(4)
        with col41:
            flu_fever = st.number_input("Flu/Fever", min_value=0, step=1)
        with col42:
            bp = st.number_input("BP", min_value=0, step=1)
        with col43:
            orthopedic_problem = st.number_input("Orthopedic", min_value=0, step=1)
        with col44:
            heart_problem = st.number_input("Heart", min_value=0, step=1)
        
        col45,col46,col47,col48 =st.columns(4)
        with col45:
            weakness = st.number_input("Weakness", min_value=0, step=1)
        with col46:
            eye_problem = st.number_input("Eye", min_value=0, step=1)
        with col47:
            accident_injuries = st.number_input("Accident Injuries", min_value=0, step=1)
        with col48:
            s_neuro = st.number_input("S_Neuro", min_value=0, step=1)
        
        col49,col50,col51,col52 =st.columns(4)
        with col49:
            piles = st.number_input("Piles", min_value=0, step=1)
        with col50:
            diabetes = st.number_input("Diabetes", min_value=0, step=1)
        with col51:
            thyroid = st.number_input("Thyroid", min_value=0, step=1)
        with col52:
            gas_problem = st.number_input("Gas", min_value=0, step=1)
        
        col53,col54,col55,col56 =st.columns(4)
        with col53:
            dental = st.number_input("Dental", min_value=0, step=1)
        with col54:
            ear = st.number_input("Ear", min_value=0, step=1)
        with col55:
            s_paralysis = st.number_input("S_Paralysis", min_value=0, step=1)
        with col56:
            general_surgery = st.number_input("General Surgery", min_value=0, step=1)
        s_total_drivers = flu_fever + bp + orthopedic_problem + heart_problem + weakness + eye_problem + accident_injuries + s_neuro + piles + diabetes + thyroid + gas_problem + dental + ear + s_paralysis + general_surgery
        s_diff =  s_total_drivers - sick_leave_S
        col20,col21=st.columns(2)
        col20.metric("Total Drivers",s_total_drivers)
        col21.metric("Diff",s_diff)
        if s_diff != 0 :
            st.error("Diff value should be equals to 0")
        
            

        notes = st.text_area("Notes")
        
        # Submit button
        submitted = st.form_submit_button("Submit Data")
        if submitted:
            insert_data((
                depot_name, entry_date, planned_schedules, planned_services, planned_km,
                actual_services, actual_km, service_variance, km_variance,
                total_drivers, medically_unfit, suspended_drivers,
                available_drivers_1, percent_available_drivers_1, weekly_off, special_off,
                other, long_leave, sick_leave_S, long_absent_A, leave_L, available_drivers_2,
                percent_available_drivers_2, spot_absent, attending_drivers, percent_attending_drivers,
                drivers_required, driver_schedule, driver_shortage, double_duty, off_cancellation,
                drivers_on_duty, drivers_as_conductors, drivers_for_bus_services, km_per_driver,
                service_driver_check, spondilitis, spinal_disc, vision_color_blindness, m_neuro,
                m_paralysis, m_total_drivers, m_diff, flu_fever, bp, orthopedic_problem,
                heart_problem, weakness, eye_problem, accident_injuries, s_neuro, piles, diabetes,
                thyroid, gas_problem, dental, ear, s_paralysis, general_surgery,
                s_total_drivers, s_diff, notes
            ))
            st.success("✅ Data submitted successfully!")
    
elif selection == "Productivity Budget 8 Ratios (Rural/Urban)":
    st.header("Productivity Budget 8 Ratios (Rural/Urban)")
    st.write("📊 View rural vs. urban productivity budget ratios.")

elif selection == "Productivity Budget vs. Actual 8 Ratios":
    st.header("Productivity Budget vs. Actual 8 Ratios")
    st.write("📈 Compare budgeted vs. actual ratios.")

elif selection == "Depot Dashboard":
    st.header("Depot Dashboard")
    st.write("🏢 Summary dashboard for depots.")
    
elif selection == "AI Depot Tool":
    st.header("AI Depot Tool")
    st.write("🤖 AI-powered depot analysis.")

elif selection == "Driver Dashboard":
    st.header("Driver Dashboard")
    st.write("🚗 Driver performance dashboard.")

st.markdown("---")
st.markdown("© 2025 TGSRTC. All rights reserved.")
