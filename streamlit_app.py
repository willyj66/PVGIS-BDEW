from EST_tidy_data import makedf
import numpy as np
import pandas as pd
import altair as alt
from io import BytesIO
import pandas as pd
import streamlit as st
import pgeocode
from PIL import Image

country = pgeocode.Nominatim("gb")
MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}
invMonthDict = {v: k for k, v in MonthDict.items()}
PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop or Barber","g5":"Bakery","g6":"Weekend Business",
    "l0":"General Farm","l1":"Dairy or Livestock Farm", "l2":"Other Farm", "h0":"Household"}
invPropertyDict = {v: k for k, v in PropertyDict.items()}

start = 2013
end = 2016
st.set_page_config(layout="wide")

#hide_streamlit_style = """
#            <style>
#            #MainMenu {visibility: hidden;}
#            footer {visibility: hidden;}
#            </style>
#            """
#st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

logo = Image.open('logo.png')
col1, col2, col3 = st.columns([4,12,1.1])
@st.cache
def to_the_shop_to_get_your_PVGIS_data(property_type,lat,lon,annual_consumption, PV_max_power, battery_capacity_kWh, surface_tilt, surface_azimuth):
    return makedf(invPropertyDict[property_type],lat, lon, annual_consumption, PV_max_power, battery_capacity_kWh, surface_tilt, surface_azimuth,start, end)

with col1:
    location = st.radio("How to imput location?",("Coordinates","Postcode"),horizontal=True,label_visibility='hidden')
    if location == "Coordinates":
        lat = float(st.text_input('Latitude', value=0))
        lon = float(st.text_input('Longitude',value=0))
    elif location == "Postcode":
        postcode = st.text_input('Postcode')
        if postcode!="":
            postcode_data = country.query_postal_code(postcode)
            lat = float(postcode_data["latitude"])
            lon = float(postcode_data["longitude"])
            st.code("Latitude  = "+str(lat)+"\nLongitude = "+str(lon))
        else:
            lat,lon=0,0
    with st.form(key="Input parameters"):
        property_type = st.selectbox('What is the property type?',PropertyDict.values())
        annual_consumption = st.number_input('Annual property consumption [kWh]',value=12000,step=1)
        PV_max_power = st.number_input('PV system peak power [kWp]',value=5.0,step=0.1)
        battery_capacity_kWh = st.number_input('Battery Capacity [kWh]',value=5.0,step=0.1, min_value=0.0)
        surface_tilt = st.number_input('Surface tilt [degrees]',value=35,step=1)
        surface_azimuth = st.number_input('Surface azimuth [degrees]',value=0,step=1)
        button = st.form_submit_button(label="Plot the plot!")
            
with col2:
    if (lon,lat) == (0,0):
        """
        # Welcome to the PVGIS-BDEW Tool!
        Made with :heart: by the Energy Saving Trust
        """
        st.markdown('<sub><sup>All errors are 95% confidence intervals (i.e. 1.96 x standard error on the mean)</sub></sup>',unsafe_allow_html=True)
        with col3:
            """##\n##"""
            st.image(logo)
    else:
        df, average,cloudy, sunny, bdew_demand, t, yearly_gen, yearly_use_pv_only, yearly_used_pv_battery = to_the_shop_to_get_your_PVGIS_data(
                    property_type,lat,lon,annual_consumption, PV_max_power, battery_capacity_kWh, surface_tilt, surface_azimuth)
        month_slider = st.select_slider("Month", MonthDict.values(),label_visibility='hidden')
        month = invMonthDict[month_slider]
        day = st.radio("What day?",('workday','saturday','sunday'),horizontal=True,label_visibility='hidden')

        # stats = ('Annual PV generation = ' + str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh\n'+
        #         'PV energy used per year (PV only) = '+str(yearly_use_pv_only[0])+' ± '+str(yearly_use_pv_only[1])+' kWh\n',
        #         'PV energy used per year (battery) = '+str(yearly_used_pv_battery[0])+' ± '+str(yearly_used_pv_battery[1])+' kWh',)
        # st.code(stats)
        
        # st.markdown(f"**Annual PV generation** = {yearly_gen[0]} ± {yearly_gen[1]} kWh")
        # st.markdown(f"**PV energy used per year (PV only)** = {yearly_use_pv_only[0]} ± {yearly_use_pv_only[1]} kWh")
        # st.markdown(f"**PV energy used per year (battery)** = {yearly_used_pv_battery[0]} ± {yearly_used_pv_battery[1]} kWh")
        
        st.markdown(f"**Annual PV generation**               = {yearly_gen[0]:<5} ± {yearly_gen[1]:<4} kWh")
        st.markdown(f"**PV energy used per year (PV only)**  = {yearly_use_pv_only[0]:<5} ± {yearly_use_pv_only[1]:<4} kWh")
        st.markdown(f"**PV energy used per year (battery)**  = {yearly_used_pv_battery[0]:<5} ± {yearly_used_pv_battery[1]:<4} kWh")
        
        table = f"""
        <table style="width:80%; text-align:left; margin: auto; border-collapse: collapse;">
            <tr>
                <td style="width:40%; border: none;"><strong>Annual PV generation</strong></td>
                <td style="width:20%; border: none;">= {yearly_gen[0]}</td>
                <td style="width:20%; border: none;">± {yearly_gen[1]}</td>
                <td style="width:20%; border: none;">kWh</td>
            </tr>
            <tr>
                <td style="width:40%; border: none;"><strong>PV energy used per year (PV only)</strong></td>
                <td style="width:20%; border: none;">= {yearly_use_pv_only[0]}</td>
                <td style="width:20%; border: none;">± {yearly_use_pv_only[1]}</td>
                <td style="width:20%; border: none;">kWh</td>
            </tr>
            <tr>
                <td style="width:40%; border: none;"><strong>PV energy used per year (battery)</strong></td>
                <td style="width:20%; border: none;">= {yearly_used_pv_battery[0]}</td>
                <td style="width:20%; border: none;">± {yearly_used_pv_battery[1]}</td>
                <td style="width:20%; border: none;">kWh</td>
            </tr>
        </table>
        """
        
        # Display the table
        st.markdown(table, unsafe_allow_html=True)
        
        PV = alt.Chart(df[month-1]).mark_line(strokeWidth=6).encode(
        x='time',
        y=alt.Y('PV generation',scale=alt.Scale(domain=(0,PV_max_power*2/3))))

        error = alt.Chart(df[month-1]).mark_area(opacity=0.2).encode(x='time',y='PV min',y2='PV max')
        if day == 'workday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW workday')
        elif day == 'saturday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW saturday')
        elif day == 'sunday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW sunday')

        chart = PV+error +BDEW
        chart.height=530
        st.altair_chart(chart,use_container_width=True)

with col3:
    if (lon,lat)!=(0,0):
        """##\n##"""
        st.image(logo)
        def export_xlsx(df):
            output = BytesIO()
            year_df = pd.DataFrame(
                index = ['a','b','c','d'],
                columns = ['Annual \nDemand: ' + str(annual_consumption)+' kWh',
                 'Annual PV \ngeneration: ' + (str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh'),
                 ('Annual PV \n used (PV only): ' + str(yearly_use_pv_only[0])+' ± '+str(yearly_use_pv_only[1])+' kWh'),
                 ('Annual PV \n used (PV and battery): ' + str(yearly_used_pv_battery[0])+' ± '+str(yearly_used_pv_battery[1])+' kWh')])
            frames = [average,cloudy,sunny,bdew_demand,year_df]
            start_row = 1
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            sheet_name='Monthly Percentages'
            for df in frames:  # assuming they're already DataFrames
                df.to_excel(writer, sheet_name, startrow=start_row, startcol=0, index=False)
                start_row += len(df) + 2  # add a row for the column header?
                for column in df:
                    column_width = max(df[column].astype(str).map(len).max(), len(column))
                    col_idx = df.columns.get_loc(column)
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)
            writer.close()
            processed_data = output.getvalue()
            return processed_data

        toexport = export_xlsx(df)
        """##\n##\n"""
        st.text("Download:\n")
        st.download_button(label='📥',
                                    data=toexport ,
                                    file_name= invPropertyDict[property_type]+"_"+str(annual_consumption)+"kWh_"+str(PV_max_power)+"kWp.xlsx")
        

        




