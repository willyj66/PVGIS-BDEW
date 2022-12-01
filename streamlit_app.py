from EST_tidy_data import makedf
#from EST_gui import get_variables
import numpy as np
import pandas as pd
from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st



MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}
PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop or Barber","g5":"Bakery","g6":"Weekend Business","g7":"Mobile Phone Transmitter Station",
    "l0":"General Farm","l1":"Dairy or Livestock Farm", "l2":"Other Farm", "h0":"Household"}

property_type, lat, lon = 'g0',56.140,-3.919
start = 2013
end = 2016

with st.form(key="Input parameters"):
    annual_consumption = st.number_input('Annual property consumption [kWh]',value=12000,step=1)
    PV_max_power = st.number_input('PV system peak power [kWp]',value=5,step=1)
    surface_tilt = st.number_input('Surface tilt [degrees]',value=35,step=1)
    surface_azimuth = st.number_input('Surface tilt [degrees]',value=0,step=1)
    st.form_submit_button(label="Submit")

df, average,cloudy, sunny, bdew_demand, t, yearly_gen, yearly_use = makedf(
    property_type,lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth,start, end
    )



"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""


with st.echo(code_location='below'):
    total_points=10
    num_turns=2
    month = st.slider("Month", 1, 12, 12)
    PV = df[month-1]['PV generation']
    #num_turns = st.slider("Number of turns in spiral", 1, 100, 9)
    source = pd.DataFrame({
        't': t,
        'y': PV
    })


    st.altair_chart(alt.Chart(pd.DataFrame(source), height=500, width=500)
        .mark_line(color='#0068c9', opacity=0.5)
        .encode(x='t', y='y'))
