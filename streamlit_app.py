from EST_tidy_data import makedf
#from EST_gui import get_variables
import numpy as np
import pandas as pd
from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import pgeocode


country = pgeocode.Nominatim("gb")
MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}
PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop or Barber","g5":"Bakery","g6":"Weekend Business",
    "l0":"General Farm","l1":"Dairy or Livestock Farm", "l2":"Other Farm", "h0":"Household"}
invPropertyDict = {v: k for k, v in PropertyDict.items()}

#lat, lon = 56.140,-3.919
start = 2013
end = 2016

"""
# Welcome to the PVGIS-BDEW Tool!
Made by Maxim Oweyssi for the Energy Saving Trust :heart:

Imput your property parameters, proposed PV install specifications, annual consumption and press Submit!
"""


@st.cache
def to_the_shop_to_get_your_PVGIS_data(property_type,lat,lon,annual_consumption, PV_max_power, surface_tilt, surface_azimuth):
    return makedf(invPropertyDict[property_type],lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth,start, end)

with st.form(key="Location parameters"):
    property_type = st.selectbox('What is the property type?',PropertyDict.values())
    location_method = st.selectbox('How would you like to input location?',('Postcode','Coordinates'))
    button = st.form_submit_button(label="Continue")

    
    
with st.form(key="Input parameters"):
    if location_method == 'Coordinates':
        lat = float(st.text_input('Latitude', value=56.140,))
        lon = float(st.text_input('Longitude',value =-3.919))
        st.experimental_rerun()
    if location_method == 'Postcode':
        postcode = st.text_input('Postcode')
        postcode_data = country.query_postal_code(postcode)
        lat = postcode_data["latitude"]
        lon = postcode_data["longitude"]
        st.experimental_rerun()
    annual_consumption = st.number_input('Annual property consumption [kWh]',value=12000,step=1)
    PV_max_power = st.number_input('PV system peak power [kWp]',value=5,step=1)
    surface_tilt = st.number_input('Surface tilt [degrees]',value=35,step=1)
    surface_azimuth = st.number_input('Surface tilt [degrees]',value=0,step=1)
    button = st.form_submit_button(label="Plot the plot!")
    if button:
        df, average,cloudy, sunny, bdew_demand, t, yearly_gen, yearly_use = to_the_shop_to_get_your_PVGIS_data(
            property_type,lat,lon,annual_consumption, PV_max_power, surface_tilt, surface_azimuth)
        month = st.slider("Month", 1, 12, 12)



        PV = df[month-1]['PV generation']
        source = pd.DataFrame({'t': t,'y': PV})
        st.altair_chart(alt.Chart(pd.DataFrame(source), height=500, width=500)
        .mark_line(color='#0068c9', opacity=0.5)
        .encode(x='t', y='y'))
        















