import streamlit as st
import fastf1 as f1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

st.title('F1 Telemetry Data Visualization')
st.sidebar.header('Select Options')

#f1.Cache.enable_cache('Cache') #Uncomment this line of code to enable caching of race data for faster loading

year = st.sidebar.number_input('Select Year', min_value=1950, max_value=2024, value=2024)
gp = st.sidebar.text_input('Enter Grand Prix Name', 'Bahrain')
session_type = st.sidebar.selectbox('Session Type', ['Q','R', 'FP1', 'FP2', 'FP3'])
driver_1 = st.sidebar.text_input('Driver 1 Code', 'HAM')
driver_2 = st.sidebar.text_input('Driver 2 Code', 'VER')

@st.cache_data
def load_session_data(year, gp, session_type):
    session = f1.get_session(year, gp, session_type)
    session.load()
    return session

placeholder = st.empty()
with placeholder:
    session = load_session_data(year, gp, session_type)

d1_name = f1.plotting.get_driver_name(driver_1,session)
d2_name = f1.plotting.get_driver_name(driver_2,session)

def get_telemetry_data(session, driver):
    telemetry = session.laps.pick_driver(driver).pick_fastest().get_telemetry()
    return pd.DataFrame(telemetry)

d1 = get_telemetry_data(session, driver_1)
d2 = get_telemetry_data(session, driver_2)

# This is done because each lap of each driver have different number of data points and speeds cannot be compared in such data.
common_index = np.union1d(d1['Distance'].values, d2['Distance'].values)
d1 = d1.set_index('Distance').reindex(common_index).interpolate().reset_index()
d2 = d2.set_index('Distance').reindex(common_index).interpolate().reset_index()

difference = []
for i in range(len(common_index)):
    if d1["Speed"][i] > d2["Speed"][i]:
        difference.append([d1["Speed"][i], "d1", d1["X"][i], d1["Y"][i]])
    else:
        difference.append([d2["Speed"][i], "d2", d2["X"][i], d2["Y"][i]])

difference_df = pd.DataFrame(difference, columns=["Speed", "Driver", "X", "Y"]).dropna()

st.header('Track Domination')
fig, ax = plt.subplots()

for i in range(len(difference_df) - 1):
    current_driver = difference_df["Driver"].iloc[i]
    x_values = [difference_df["X"].iloc[i], difference_df["X"].iloc[i + 1]]
    y_values = [difference_df["Y"].iloc[i], difference_df["Y"].iloc[i + 1]]
    color = 'blue' if current_driver == 'd1' else 'red'
    ax.plot(x_values, y_values, color=color, linewidth=4)

driver_colors = {}
legend_elements = [Line2D([0], [0], color='blue', lw=4, label=d1_name),
                   Line2D([0], [0], color='red', lw=4, label=d2_name)]
ax.legend(handles=legend_elements)
plt.axis("off")
st.pyplot(fig)
d1_count = difference_df["Driver"].value_counts()["d1"]
d2_count = difference_df["Driver"].value_counts()["d2"]
st.write(f"{d1_name} dominated {((d1_count/len(difference_df))*100).round(1)}% of the Track")
st.write(f"{d2_name} dominated {((d2_count/len(difference_df))*100).round(1)}% of the Track")