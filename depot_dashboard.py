import streamlit as st
import pandas as pd
import altair as alt

# --- Config ---
DEPOTS = ['kmm', 'adb', 'hyd2', 'srd', 'mlg', 'kmr', 'jgit', 'flk', 'mhbd', 'mbnr', 'rng']
HEALTH_MAP = {'A': 95, 'B': 85, 'C': 75, 'D': 60, 'E': 50}  # Add E if needed

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel(r"C:\Users\Thaduriomprakash\Desktop\DAILY_DATA\TGSRTC_AIProject_Absenteeism_All_KMM.xlsx")
    df['depot'] = df['depot'].str.lower()
    df['health_numeric'] = df['health_score'].map(HEALTH_MAP)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("Filters")

# Depot Filter
selected_depot = st.sidebar.selectbox("Select Depot", DEPOTS)

# Filter by Depot
filtered_df = df[df['depot'] == selected_depot]

# Driver Filter (after depot is selected)
driver_ids = filtered_df['employee_id'].unique()
selected_driver = st.sidebar.selectbox("Select Driver ID", driver_ids)

# Get selected driver data
driver_data = filtered_df[filtered_df['employee_id'] == selected_driver].iloc[0]

# --- Dashboard Display ---
st.title("TGSRTC Driver Productivity & Health Snapshot")
st.subheader(f"Driver: {driver_data['driver_name']} (ID: {driver_data['employee_id']})")
st.text(f"Depot: {driver_data['depot'].upper()}")
col1,col2,col3=st.columns(3)
# Metrics
with col1:
    st.metric("KM Driven", f"{driver_data['km_driven']} km")
with col2:
    st.metric("Leaves Taken", f"{driver_data['leaves_taken']} days")
with col3:
    st.metric("Health Score", f"{driver_data['health_score']} ({driver_data['health_numeric']}/100)")

# Health Grade Interpretation
if driver_data['health_numeric'] >= 90:
    grade = "Excellent"
elif driver_data['health_numeric'] >= 85:
    grade = "Good"
elif driver_data['health_numeric'] >= 70:
    grade = "Average"
elif driver_data['health_numeric'] >= 60:
    grade = "Bad"
else:
    grade = "Needs Attention"

st.info(f"*Health Grade:* {grade}")

# Highlight 'health_score' if grade is D
def highlight_health_grade(val):
    if val == 'D':
        return 'background-color: red; color: white; font-weight: bold'
    return ''

# Highlight 'km_driven' if below threshold
def highlight_low_km(val):
    if isinstance(val, (int, float)) and val < 9000:
        return 'background-color: orange; color: black; font-weight: bold'
    return ''

# Highlight entire row for selected driver
def highlight_selected_row(row):
    return ['background-color: Green' if row['employee_id'] == selected_driver else '' for _ in row]

with st.expander("View All Drivers in Selected Depot"):
    styled_df = (
        filtered_df.style
        .applymap(highlight_health_grade, subset=['health_score'])
        .applymap(highlight_low_km, subset=['km_driven'])
        .apply(highlight_selected_row, axis=1)
    )
    st.dataframe(styled_df)




# --- Driver Averages in Depot ---
avg_df = (
    filtered_df.groupby(['employee_id'], as_index=False)
    .agg({'leaves_taken': 'mean', 'km_driven': 'mean'})
    .rename(columns={'leaves_taken': 'avg_leaves', 'km_driven': 'avg_kms'})
)

# Add a highlight flag
avg_df['is_selected'] = avg_df['employee_id'] == selected_driver

# Bar chart for Average Leaves Taken
st.subheader("Average Leaves Taken per Driver")
lsa_chart = alt.Chart(avg_df).mark_bar().encode(
    x=alt.X('employee_id:N', sort='-y', title='Employee ID'),
    y=alt.Y('avg_leaves:Q', title='Avg Leaves Taken'),
    color=alt.condition(
        alt.datum.is_selected,
        alt.value('crimson'),     # Highlighted bar
        alt.value('steelblue')    # Default bar
    ),
    tooltip=['employee_id', 'avg_leaves']
).properties(width=700, height=400)
st.altair_chart(lsa_chart, use_container_width=True)

# Bar chart for Average Kilometers Driven
st.subheader("Average Kilometers Driven per Driver")
km_chart = alt.Chart(avg_df).mark_bar().encode(
    x=alt.X('employee_id:N', sort='-y', title='Employee ID'),
    y=alt.Y('avg_kms:Q', title='Avg KM Driven'),
    color=alt.condition(
        alt.datum.is_selected,
        alt.value('crimson'),
        alt.value('seagreen')
    ),
    tooltip=['employee_id', 'avg_kms']
).properties(width=700, height=400)
st.altair_chart(km_chart, use_container_width=True)