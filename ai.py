import streamlit as st
import mysql.connector

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pr@k@sh9347",
    database="DAILY_SCHEDULE_AND_DRIVER_DATA"
)
cursor = conn.cursor()
cursor.execute("SELECT emp_id FROM driver_input")
emp_ids = [row[0] for row in cursor.fetchall()]
selected_emp_id = st.selectbox("Select Employee ID", emp_ids)
# Fetch data for the selected employee
cursor.execute("SELECT * FROM driver_input WHERE emp_id = %s", (selected_emp_id,))
emp_data = cursor.fetchone()
st.title("🚦 Driver Productivity Predictor")
st.subheader("Predicting driver productivity in hours based on health & operational parameters")
st.markdown("### 🩺 Driver Health and Productivity Inputs")

# Medical inputs
emp_id = 290912
age = st.slider("Age",30 , 70, 45)
creatinine = st.selectbox("Creatinine", ["Normal", "Abnormal"])
bp = st.selectbox("Blood Pressure (BP)", ["Normal", "Elevated", "Stage-1 Hypertension", "Stage-2 Hypertension", "Hypertension Critical"])
glucose = st.selectbox("Glucose", ["Normal", "Predetermine", "Diabetes"])
bilirubin = st.selectbox("Bilirubin", ["Normal", "High"])
cholesterol = st.selectbox("Cholesterol", ["Normal", "Borderline", "High"])
ecg = st.selectbox("ECG", ["Within Limits", "Abnormal"])

st.markdown("### 📆 Driver Shift and Schedule Metrics")
night_shift = st.slider("Night Shift %", 0, 100, 20)
palle = st.slider("Pallevelugu Schedules %", 0, 100, 25)
city_ord = st.slider("City Ordinary %", 0, 100, 30)
metro = st.slider("Metro Express %", 0, 100, 25)

# Simple productivity calculation based on inputs
def calculate_productivity(age, creatinine, bp, glucose, bilirubin, cholesterol, ecg, night_shift, palle, city_ord, metro):
    # Assign scores to each parameter (lower scores are better)
    age_score = (age - 35) / 10
    creatinine_score = 0 if creatinine == "Normal" else 1
    bp_score = ["Normal", "Elevated", "Stage-1 Hypertension", "Stage-2 Hypertension", "Hypertension Critical"].index(bp)
    glucose_score = ["Normal", "Predetermine", "Diabetes"].index(glucose)
    bilirubin_score = 0 if bilirubin == "Normal" else 1
    cholesterol_score = ["Normal", "Borderline", "High"].index(cholesterol)
    ecg_score = 0 if ecg == "Within Limits" else 1
    night_shift_score = night_shift / 100
    palle_score = palle / 100
    city_ord_score = city_ord / 100
    metro_score = metro / 100

    # Calculate overall score
    overall_score = age_score + creatinine_score + bp_score + glucose_score + bilirubin_score + cholesterol_score + ecg_score + night_shift_score + palle_score + city_ord_score + metro_score

    # Map overall score to productivity (lower scores result in higher productivity)
    productivity = 100000 - (overall_score * 1000)

    return max(productivity, 50000)  # Ensure productivity doesn't go below 50,000 km

# Save to MySQL and calculate productivity
if st.button("Submit & Predict"):
    insert_query = """INSERT INTO driver_input (emp_id,age, creatinine, bp, glucose, bilirubin, cholesterol, ecg, night_shift, pallevelugu, city_ordinary, metro_express)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (emp_id,age, creatinine, bp, glucose, bilirubin, cholesterol, ecg, night_shift, palle, city_ord, metro)
    cursor.execute(insert_query, values)
    conn.commit()
    st.success("✅ Data saved to MySQL successfully!")

    productivity = calculate_productivity(age, creatinine, bp, glucose, bilirubin, cholesterol, ecg, night_shift, palle, city_ord, metro)
    st.write(f"🛣 *Annual Driver Productivity (in Kilometers): {productivity}*")