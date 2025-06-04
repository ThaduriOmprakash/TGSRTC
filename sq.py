import streamlit as st
import mysql.connector
from datetime import date,timedelta



import pandas as pd
from mysql.connector import Error

# Page setup
st.set_page_config(page_title="SQ", layout="wide")
st.title("TGSRTC PRODUCTIVITY DASHBOARD")

# Sidebar menu
menu = [
    "Daily Depot Input Sheet",
    "Productivity Budget 8 Ratios (Rural/Urban)",
    "Productivity Budget vs. Actual 8 Ratios",
    "Depot Dashboard",
    "AI Depot Tool",
    "Driver Dashboard"
]
selection = st.sidebar.selectbox("Select Screen", menu)

# Database connection
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pr@k@sh9347",
            database="DAILY_SCHEDULE_AND_DRIVER_DATA"
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Load depot settings from 'AI' table
def get_depot_settings():
    conn = get_connection()
    if conn is None:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM AI")
        rows = cursor.fetchall()
        return {row["depot_name"]: row for row in rows}
    except Error as e:
        st.error(f"Error fetching depot settings: {e}")
        return {}
    finally:
        conn.close()
# Function to fetch last 10 entries for a depot
def fetch_last_10_entries(table_name):
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM depot_data
            WHERE depot_name =%s
            ORDER BY entry_date DESC
            LIMIT 10
        """
        cursor.execute(query,(depot_name,))
        result = cursor.fetchall()
        return result # Optional: show oldest first
    except Error as e:
        st.error(f"Error fetching last 10 entries: {e}")
        return None
    finally:
        conn.close()

# Main Screen
if selection == "Daily Depot Input Sheet":
    st.header("DAILY SCHEDULE AND DRIVER DATA")
    st.markdown("### 📝 Enter New Record")

        # Depot settings
    
    depot_config = get_depot_settings()

    depot_list = sorted(depot_config.keys())
    depot_options = ["Select Depot"] + depot_list

    # Create columns
    col54, col55, col56 = st.columns([3, 1.5, 3])

    with col54:
        depot_name = st.selectbox("Select Depot", depot_options)

    with col56:
        selected_date = st.date_input("Select Date", date.today())
    

    # Initialize defaults
    planned_schedules = 0
    planned_services = 0
    planned_km = 0
    category = ""
    if depot_name == "Select Depot":
        st.info("#### SELECT DEPOT")
    
     # Handle depot selection and fetch details
    if depot_name != "Select Depot":
        settings = depot_config.get(depot_name, {})
        planned_schedules = settings.get("planned_schedules", 0)
        planned_services = settings.get("planned_services", 0)
        planned_km = settings.get("planned_km", 0)
        category = settings.get("category", "")  # Fetched from DB

    # Display Category - always visible
        with col55:
            st.markdown("<div style='padding-top: 12px; font-weight: 600;'>Depot Category:</div>", unsafe_allow_html=True)
            if depot_name == "Select Depot":
                st.markdown("<div style='background-color: #660000; color: white; padding: 6px 12px; border-radius: 5px; display: inline-block;'>Select the depot</div>", unsafe_allow_html=True)
            elif category:
                st.markdown(f"<div style='background-color: #004d00; color: white; padding: 6px 12px; border-radius: 5px; display: inline-block;'>{category}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background-color: #5c5c5c; color: white; padding: 6px 12px; border-radius: 5px; display: inline-block;'>Not Available</div>", unsafe_allow_html=True)

            


        st.header(f"📆 Schedules - {category}")

        # ✅ Show last 10 entries in expander (only if a depot is selected)
        if depot_name != "Select Depot":
            last_10_entries = fetch_last_10_entries(depot_name)
            if last_10_entries and len(last_10_entries) > 0:
                with st.expander("📌 View Last 10 Entries for this Depot"):
                    st.dataframe(last_10_entries)
            else:
                st.info("No previous data found for this depot.")
        
        col1, col2, col3,col4,col5= st.columns(5)

        with col1:
            st.metric("Planned Schedules", planned_schedules)
            
            
        with col2:
            st.metric("Planned Services", planned_services)
            st.metric("Planned KM", planned_km)
            

        with col3:
            actual_services = st.number_input("Actual Services", min_value=0)
            actual_km = st.number_input("Actual KM", min_value=0)
            
        with col4:
            service_variance = actual_services - planned_services
            km_variance = actual_km - planned_km
            st.metric("Service Variance", service_variance)
            st.metric("KM Variance", km_variance)    
            
        st.markdown("### 👥 Drivers")
        col6,col7,col8 =st.columns(3)
        
        with col6:
            total_drivers = st.number_input("Total Drivers", min_value=0)
        with col7:
            
            medically_unfit = st.number_input("Medically Unfit", min_value=0)
        with col8:
            suspended_drivers = st.number_input("Suspended Drivers", min_value=0)
        with col6:
            available_drivers_1 = total_drivers - medically_unfit - suspended_drivers
            st.metric("Available Drivers-1", available_drivers_1)
        with col7:
                percent_available_drivers_1 = round((available_drivers_1 / total_drivers * 100), 2) if total_drivers else 0.0
                st.metric("% Available Drivers-1", f"{percent_available_drivers_1}%")   
            
        with col6:
            available_drivers_1 = total_drivers - medically_unfit - suspended_drivers
            
        
            
        col9,col10,col11 =st.columns(3)
        
        
        with col9:
                weekly_off = st.number_input("Weekly Off", min_value=0)
                Day_weekly_off_Benchmark =14
                Mon_weekly_off_per = 0.0
                Day_weekly_off_per = round((weekly_off/ total_drivers * 100), 2) if total_drivers else 0.0 
                st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>%weekly off</div>
                            <div style='font-size:28px'>{Day_weekly_off_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Day_weekly_off_Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)

                
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (weekly_off / total_drivers) * 100 AS percent_weekly_off
                    FROM depot_data
                    WHERE depot_name = %s AND total_drivers > 0 AND weekly_off IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                # Calculate average of these percentages
                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_weekly_off_per = round(sum(percentages) / len(percentages), 2)
                    with col9:
                        st.markdown(f" % Weekly Off (Last 30 Entries AVG): {Mon_weekly_off_per}%") 
                        
                else:
                    with col9:  
                        st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching weekly off percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        with col10:
            special_off = st.number_input("Special Off (Night Out/IC, Online)", min_value=0)
            Mon_special_off_per = 0.0
            if category == "Urban":
                Benchmark = 20.7
            else:
                Benchmark = 68
            Day_special_off_per = round((special_off/ total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>%special off</div>
                            <div style='font-size:28px'>{Day_special_off_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)    
        
            try:
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()

                    query = f"""
                        SELECT (special_off / total_drivers) * 100 AS percent_special_off
                        FROM depot_data
                        WHERE  depot_name = %s AND total_drivers > 0 AND special_off IS NOT NULL
                        ORDER BY entry_date DESC
                        LIMIT 30
                    """
                    cursor.execute(query,(depot_name,))
                    rows = cursor.fetchall()

                    # Calculate average of these percentages
                    percentages = [row[0] for row in rows if row[0] is not None]
                    if percentages:
                        Mon_special_off_per = round(sum(percentages) / len(percentages), 2)
                        with col10:
                            st.markdown(f"% Special Off (Last 30 Entries AVG): {Mon_special_off_per}%")
                            
                    else:
                        with col10:
                            st.warning("⚠️ No data found in the last 30 entries.")
            except Error as e:
                st.error(f"❌ Error fetching special off percentages: {e}")
            finally:
                if conn:
                    cursor.close()
                    conn.close()
                    
        with col11:
            other = st.number_input("Others & OD", min_value=0)
            Mon_other_per = 0.0
            Benchmark = 2.0
            Day_other_per = round((other / total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>%Others & OD</div>
                            <div style='font-size:28px'>{Day_other_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)    

        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (`other` / total_drivers) * 100 AS percent_other
                    FROM depot_data
                    WHERE  depot_name =%s  AND total_drivers > 0 AND `other` IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_other_per = round(sum(percentages) / len(percentages), 2)
                    with col11:
                        st.markdown(f"% Others & OD (Last 30 Entries  AVG): {Mon_other_per}%")
                        
                else:
                    with col11:
                        st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching Others & OD percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        col12,col13 =st.columns(2)
        with col12:
            leave_absent = st.number_input("Leave & Absent", min_value=0)
            Mon_leave_absent_per = 0.0
            Benchmark = 5.0
            Day_leave_absent_per = round((leave_absent / total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>%Leave & Absent</div>
                            <div style='font-size:28px'>{Day_leave_absent_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)  
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (leave_absent / total_drivers) * 100 AS percent_leave
                    FROM depot_data
                    WHERE  depot_name =%s AND total_drivers > 0 AND leave_absent  IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_leave_absent_per = round(sum(percentages) / len(percentages), 2)
                    with col12:
                        st.markdown(f"% Leave & Absent (Last 30 Entries AVG): {Mon_leave_absent_per}%")
                        
                else:
                    with col12:
                        st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching Leave & Absent percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        with col13:
            sick_leave = st.number_input("Sick Leave", min_value=0)
            Benchmark = 4.0
            Mon_sick_leave_per = 0.0
            Day_sick_leave_per = round((sick_leave / total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>% Sick Leave</div>
                            <div style='font-size:28px'>{Day_sick_leave_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)  
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (sick_leave / total_drivers) * 100 AS percent_sick
                    FROM depot_data
                    WHERE  depot_name =%s AND total_drivers > 0 AND sick_leave  IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_sick_leave_per = round(sum(percentages) / len(percentages), 2)
                    with col13:
                        st.markdown(f"% Sick Leave (Last 30 Entries AVG): {Mon_sick_leave_per}%")
                else:
                    with col13:
                        st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching Sick Leave percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        col14,col15 =st.columns(2)
        
        with col14:
            available_drivers_2 = available_drivers_1 - (weekly_off + special_off + other + leave_absent + sick_leave)
            st.metric("Available Drivers-2", available_drivers_2)
        with col15:
            percent_available_drivers_2 = (available_drivers_2 / total_drivers * 100) if total_drivers else 0.0    
            st.metric("% Available Drivers-2", f"{percent_available_drivers_2:.2f}%")
        spot_absent = st.number_input("Spot Absent", min_value=0)
        Mon_spot_absent_per = 0.0
        s_Benchmark = 2.0
        Day_spot_absent_per = round((spot_absent / total_drivers * 100), 2) if total_drivers else 0.0 
        st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>% Spot Absent</div>
                            <div style='font-size:28px'>{ Day_spot_absent_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {s_Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (spot_absent / total_drivers) * 100 AS percent_sick
                    FROM depot_data
                    WHERE  depot_name =%s AND total_drivers > 0 AND spot_absent  IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_spot_absent_per = round(sum(percentages) / len(percentages), 2)
                    
                    st.markdown(f"% Spot Absent (Last 30 Entries AVG): {Mon_spot_absent_per}%")
                    
                else:
                    st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching Spot Absent percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        col16,col17,col18 =st.columns(3)
        
        with col16:
            attending_drivers = available_drivers_2 - spot_absent
            st.metric("Attending Drivers", attending_drivers)
        with col17:
            percent_attending_drivers = (attending_drivers / total_drivers * 100) if total_drivers else 0.0    
            st.metric("% Attending Drivers", f"{percent_attending_drivers:.2f}%")
        col19,col20,col21 = st.columns(3)
        
        with col19:
            drivers_required = st.number_input("Drivers Required", min_value=0)
        with col20:
                driver_schedule = (drivers_required / planned_schedules) if planned_schedules else 0.0
                st.metric("Driver schedule",driver_schedule) 
        with  col21:
            driver_shortage = 0
            if drivers_required > attending_drivers:
                driver_shortage = drivers_required - attending_drivers        
            st.metric("Driver shortage",driver_shortage) 
        col22,col23 =st.columns(2)
        
        
        with col22:
            double_duty = st.number_input("Double Duty", min_value=0)
            if category == "Urban":
                Benchmark = 4.0
            else:
                Benchmark = 10.0
            Mon_double_duty_per = 0.0
            Day_double_duty_per = round((double_duty / total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>% Double Duty</div>
                            <div style='font-size:28px'>{Day_double_duty_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)
        
            try:
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()

                    query = f"""
                        SELECT (double_duty / total_drivers) * 100 AS percent_double_duty
                        FROM depot_data
                        WHERE depot_name =%s AND total_drivers > 0 AND double_duty  IS NOT NULL
                        ORDER BY entry_date DESC
                        LIMIT 30
                    """
                    cursor.execute(query,(depot_name,))
                    rows = cursor.fetchall()

                    percentages = [row[0] for row in rows if row[0] is not None]
                    if percentages:
                        Mon_double_duty_per = round(sum(percentages) / len(percentages), 2)
                        with col22:
                            st.markdown(f"% Double Duty (Last 30 Entries AVG): {Mon_double_duty_per}%")
                    else:
                        with col22:
                            st.warning("⚠️ No data found in the last 30 entries.")
            except Error as e:
                st.error(f"❌ Error fetching Double Duty percentages: {e}")
            finally:
                if conn:
                    cursor.close()
                    conn.close()
            
        with col23:
            off_cancellation = st.number_input("Off Cancellation", min_value=0)
            Mon_off_cancellation_per = 0.0
            Benchmark=  2.0
            Day_off_cancellation_per = round((off_cancellation/ total_drivers * 100), 2) if total_drivers else 0.0 
            st.markdown(
                            f"""
                            <div style='font-size:22px; font-weight:bold'>% Off Cancellation</div>
                            <div style='font-size:28px'>{Day_off_cancellation_per}%</div>
                            <div style='font-size:14px; color:gray'>Benchmark: {Benchmark}%</div>
                            """,
                            unsafe_allow_html=True
)
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()

                query = f"""
                    SELECT (off_cancellation / total_drivers) * 100 AS percent_off_cancellation
                    FROM depot_data
                    WHERE  depot_name =%s AND total_drivers > 0 AND off_cancellation  IS NOT NULL
                    ORDER BY entry_date DESC
                    LIMIT 30
                """
                cursor.execute(query,(depot_name,))
                rows = cursor.fetchall()

                percentages = [row[0] for row in rows if row[0] is not None]
                if percentages:
                    Mon_off_cancellation_per = round(sum(percentages) / len(percentages), 2)
                    with col23:
                        st.markdown(f"% Off Cancellation (Last 30 Entries AVG): {Mon_off_cancellation_per}%")
                        
                else:
                    with col23:
                        st.warning("⚠️ No data found in the last 30 entries.")
        except Error as e:
            st.error(f"❌ Error fetching Off Cancellation percentages: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        col24,col25,col26,col27,col28 =st.columns(5)
        
        with col24:
            drivers_as_conductors = st.number_input("Drivers as Conductors", min_value=0)
        with col25:
            drivers_on_duty = attending_drivers + double_duty + off_cancellation
            st.metric("Drivers on Duty",drivers_on_duty) 
        with col26:
            drivers_for_bus_services = drivers_on_duty - drivers_as_conductors
            st.metric("Driver for Bus Services",drivers_for_bus_services)    
        with col27:
            km_per_driver = (actual_km / drivers_for_bus_services) if drivers_for_bus_services else 0.0
            st.metric("KM/Driver",km_per_driver)  
        with col28:
            service_driver_check = drivers_for_bus_services - actual_services
            st.metric("Service/Driver Check",service_driver_check) 
            
            
        st.markdown("### Medically Unfit - Reasons")
        col29,col30,col31,col32,col33 =st.columns(5)   
        with col29:
            spondilitis = st.number_input("Spondilitis", min_value=0, step=1)
        with col30:
            spinal_disc = st.number_input("Spinal Disc", min_value=0, step=1)
        with col31:
            vision_color_blindness = st.number_input("Vision/Color Blindness", min_value=0, step=1)
        with col32:
            m_neuro = st.number_input("Neuro", min_value=0, step=1)
        with col33:
            m_paralysis = st.number_input("Paralysis", min_value=0, step=1)
        m_total_drivers = spondilitis + spinal_disc +  vision_color_blindness +  m_neuro + m_paralysis
        m_diff = m_total_drivers - medically_unfit
        col34,col35=st.columns(2)
        with col34:
            col34.metric("Total Drivers",m_total_drivers)
        with col35:
            col35.metric("Diff",m_diff)

        if m_diff != 0 :
            st.error("Diff value should be equals to 0")
        st.markdown("### Sick Leave - Reasons")
        col36,col37,col38,col39,col40,col41,col42 =st.columns(7)
        with col36:
            flu_fever = st.number_input("Flu/Fever", min_value=0)
        with col37:
            bp = st.number_input("BP", min_value=0)
        with col38:
            orthopedic_problem = st.number_input("Orthopedic", min_value=0)
        with col39:
            heart_problem = st.number_input("Heart", min_value=0)
        with col40:
            weakness = st.number_input("Weakness", min_value=0)
        with col41:
            eye_problem = st.number_input("Eye", min_value=0)
        with col42:
            accident_injuries = st.number_input("Accident Injuries", min_value=0)  
                    
        col43,col44,col45,col46,col47,col48,col49,col50,col51=st.columns(9)
        
        with col43:
            s_neuro = st.number_input("S_Neuro", min_value=0)
        with col44:
            piles = st.number_input("Piles", min_value=0)
        with col45:
            diabetes = st.number_input("Diabetes", min_value=0)
        with col46:
            thyroid = st.number_input("Thyroid", min_value=0)
        with col47:
            gas_problem = st.number_input("Gas", min_value=0)
        with col48:
            dental = st.number_input("Dental", min_value=0)
        with col49:
            ear = st.number_input("Ear", min_value=0)
        with col50:
            s_paralysis = st.number_input("S_Paralysis", min_value=0)
        with col51:
            general_surgery = st.number_input("General Surgery", min_value=0)
            
        s_total_drivers = flu_fever + bp + orthopedic_problem + heart_problem + weakness + eye_problem + accident_injuries + s_neuro + piles + diabetes + thyroid + gas_problem + dental + ear + s_paralysis + general_surgery
        s_diff =  s_total_drivers - sick_leave
        
        col52,col53=st.columns(2)
        with col52:
            st.metric("Total Drivers",s_total_drivers)
        with col53:
            st.metric("Diff",s_diff)
        if s_diff != 0 :
            st.error("Diff value should be equals to 0")                                                                     
    # Submit button
        if st.button("✅ Submit Data"):
            conn = get_connection()
            if conn:
                try:
                    cursor = conn.cursor()

                    insert_query = f"""
                        INSERT INTO depot_data (
                            entry_date, depot_name, category, planned_schedules, planned_services, planned_km,
                            actual_services, actual_km, service_variance, km_variance,total_drivers,
                            medically_unfit, suspended_drivers,available_drivers_1,percent_available_drivers_1,
                            weekly_off,Day_weekly_off_per, special_off,Day_special_off_per,other,Day_other_per,leave_absent,
                            Day_leave_absent_per,sick_leave,Day_sick_leave_per,available_drivers_2,percent_available_drivers_2,
                            spot_absent,Day_spot_absent_per,attending_drivers,percent_attending_drivers,drivers_required,driver_schedule,
                            driver_shortage,double_duty,Day_double_duty_per,off_cancellation,Mon_off_cancellation_per,drivers_on_duty,
                            drivers_as_conductors,drivers_for_bus_services,km_per_driver,service_driver_check,spondilitis,spinal_disc,
                            vision_color_blindness,m_neuro,m_paralysis,m_total_drivers,m_diff,flu_fever,bp,orthopedic_problem,heart_problem,
                            weakness,eye_problem,accident_injuries,s_neuro,piles,diabetes,thyroid,gas_problem,dental,ear,s_paralysis,general_surgery,
                            s_total_drivers,s_diff
                            
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    values = (
                        selected_date,depot_name, category, planned_schedules, planned_services, planned_km,
                            actual_services, actual_km, service_variance, km_variance,total_drivers,
                            medically_unfit, suspended_drivers,available_drivers_1,percent_available_drivers_1,
                            weekly_off,Day_weekly_off_per, special_off,Day_special_off_per,other,Day_other_per,leave_absent,
                            Day_leave_absent_per,sick_leave,Day_sick_leave_per,available_drivers_2,percent_available_drivers_2,
                            spot_absent,Day_spot_absent_per,attending_drivers,percent_attending_drivers,drivers_required,driver_schedule,
                            driver_shortage,double_duty,Day_double_duty_per,off_cancellation,Mon_off_cancellation_per,drivers_on_duty,
                            drivers_as_conductors,drivers_for_bus_services,km_per_driver,service_driver_check,spondilitis,spinal_disc,
                            vision_color_blindness,m_neuro,m_paralysis,m_total_drivers,m_diff,flu_fever,bp,orthopedic_problem,heart_problem,
                            weakness,eye_problem,accident_injuries,s_neuro,piles,diabetes,thyroid,gas_problem,dental,ear,s_paralysis,general_surgery,
                            s_total_drivers,s_diff
                    )
                    cursor.execute(insert_query, values)
                    conn.commit()
                    st.success("✅ Data inserted into MySQL successfully!")
                except Error as e:
                    st.error(f"❌ Failed to insert data: {e}")
                finally:
                    cursor.close()
                    conn.close()
            else:
                st.error("❌ No database connection established.")