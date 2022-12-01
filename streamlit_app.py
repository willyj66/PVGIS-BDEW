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

property_type, lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth = 'g0',56.140,-3.919,12000,8,0,35
start = 2013
end = 2016

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
    total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
    num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

    Point = namedtuple('Point', 'x y')
    data = []

    points_per_turn = total_points / num_turns

    for curr_point_num in range(total_points):
        curr_turn, i = divmod(curr_point_num, points_per_turn)
        angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
        radius = curr_point_num / total_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        data.append(Point(x, y))

    st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
        .mark_circle(color='#0068c9', opacity=0.5)
        .encode(x='x:Q', y='y:Q'))
