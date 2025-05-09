from EST_BDEW import get_BDEW
from EST_PVGIS import get_PV_Data, get_Wind_Data, CalculateBatterySavings
import numpy as np
import pandas as pd

MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}

PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop / Barber","g5":"Bakery",	 "g6":"Weekend Business","g7":"Mobile Phone Transmitter Station",
    "l0":"General Farm","l1":"Dairy / Livestock Farm", "l2":"Other Farm", "h0":"Household"}

def process_data(calc_type, generation_data, battery_capacity_kWh, property_type, annual_consumption):
        
    if calc_type == "Wind":
        min_name = "Still"
        max_name = "Windy"
    elif calc_type == "PV":
        min_name = "Cloudy"
        max_name = "Sunny"

    generation_hourly, error_hourly, yearly_generation, yearly_used_generation_only, yearly_used_generation_battery, full_hh_data  = CalculateBatterySavings(
        generation_data, battery_capacity_kWh, property_type, annual_consumption
        )
    time_hourly = np.linspace(0,24,24)
    time = np.linspace(0,24,24*4)
    workday, saturday, sunday = get_BDEW(property_type,2022,annual_consumption)
    df_list = []
    bdew_demand = {
        "Month": [],
        "Workday\n Demand [kWh]": [],
        "Saturday\n Demand [kWh]": [],
        "Sunday\n Demand [kWh]": [],
    }
    average = {
        "Month": [],
        f"{calc_type}\n Generation [kWh]": [],
        f"Workday Demand\n Covered by {calc_type}": [],
        f"Saturday Demand\n Covered by {calc_type}": [],
        f"Sunday Demand\n Covered by {calc_type}": [],
        f"Workday {calc_type}\n Used by Demand": [],
        f"Saturday {calc_type}\n Used by Demand": [],
        f"Sunday {calc_type}\n Used by Demand": [],
    }
    min = {
        "Month": [],
        f"{min_name}\n {calc_type}\n Generation [kWh]": [],
        f"{min_name}\n Workday Demand\n Covered by {calc_type}": [],
        f"{min_name}\n Saturday Demand\n Covered by {calc_type}": [],
        f"{min_name}\n Sunday Demand\n Covered by {calc_type}": [],
        f"{min_name}\n Workday {calc_type}\n Used by Demand": [],
        f"{min_name}\n Saturday {calc_type}\n Used by Demand": [],
        f"{min_name}\n Sunday {calc_type}\n Used by Demand": [],
    }
    max = {
        "Month": [],
        f"{max_name}\n {calc_type}\n Generation [kWh]": [],
        f"{max_name}\n Workday Demand\n Covered by {calc_type}": [],
        f"{max_name}\n Saturday Demand\n Covered by {calc_type}": [],
        f"{max_name}\n Sunday Demand\n Covered by {calc_type}": [],
        f"{max_name}\n Workday {calc_type}\n Used by Demand": [],
        f"{max_name}\n Saturday {calc_type}\n Used by Demand": [],
        f"{max_name}\n Sunday {calc_type}\n Used by Demand": [],
    }

    for month in range(12):
        df=pd.DataFrame()

        """Convert PVGIS data to 15 minute resolution"""
        error = np.interp(time,time_hourly,error_hourly[month])
        generation = np.interp(time,time_hourly,generation_hourly[month])
        generation_min = generation-2*error
        generation_max = generation+2*error

        """Find % of demand covered by PV"""
        workday_intersection        = np.trapezoid(np.amin([workday[month],generation], axis=0),time)/4
        saturday_intersection       = np.trapezoid(np.amin([saturday[month],generation], axis=0),time)/4
        sunday_intersection         = np.trapezoid(np.amin([sunday[month],generation], axis=0),time)/4

        min_workday_intersection    = np.trapezoid(np.amin([workday[month],generation_min], axis=0),time)/4
        min_saturday_intersection   = np.trapezoid(np.amin([saturday[month],generation_min], axis=0),time)/4
        min_sunday_intersection     = np.trapezoid(np.amin([sunday[month],generation_min], axis=0),time)/4

        max_workday_intersection    = np.trapezoid(np.amin([workday[month],generation_max], axis=0),time)/4
        max_saturday_intersection   = np.trapezoid(np.amin([saturday[month],generation_max], axis=0),time)/4
        max_sunday_intersection     = np.trapezoid(np.amin([sunday[month],generation_max], axis=0),time)/4

        total_generation            = np.trapezoid(generation,time)/4
        total_min_generation        = np.trapezoid(generation_min,time)/4
        total_max_generation        = np.trapezoid(generation_max,time)/4

        workday_demand              = np.trapezoid(workday[month],time)/4
        saturday_demand             = np.trapezoid(saturday[month],time)/4
        sunday_demand               = np.trapezoid(sunday[month],time)/4

        workday_demand_covered      = 100*workday_intersection/workday_demand
        saturday_demand_covered     = 100*saturday_intersection/saturday_demand
        sunday_demand_covered       = 100*sunday_intersection/sunday_demand

        min_workday_demand_covered  = 100*min_workday_intersection/workday_demand
        min_saturday_demand_covered = 100*min_saturday_intersection/saturday_demand
        min_sunday_demand_covered   = 100*min_sunday_intersection/sunday_demand

        max_workday_demand_covered  = 100*max_workday_intersection/workday_demand
        max_saturday_demand_covered = 100*max_saturday_intersection/saturday_demand
        max_sunday_demand_covered   = 100*max_sunday_intersection/sunday_demand


        """Find % of PV output used"""
        workday_generation_used        = 100*workday_intersection/total_generation
        saturday_generation_used       = 100*saturday_intersection/total_generation
        sunday_generation_used         = 100*sunday_intersection/total_generation
    
        min_workday_generation_used    = 100*min_workday_intersection/total_min_generation
        min_saturday_generation_used   = 100*min_saturday_intersection/total_min_generation
        min_sunday_generation_used     = 100*min_sunday_intersection/total_min_generation

        max_workday_generation_used    = 100*max_workday_intersection/total_max_generation
        max_saturday_generation_used   = 100*max_saturday_intersection/total_max_generation
        max_sunday_generation_used     = 100*max_sunday_intersection/total_max_generation
        

        """Write time-data into Pandas data frame"""
        df = pd.DataFrame({
            'time'             : time,
            'Total generation' : generation,
            'Gen min'          : generation_min,
            'Gen max'          : generation_max,
            'BDEW workday'     : workday[month],
            'BDEW saturday'    : saturday[month],
            'BDEW sunday'      : sunday[month]

        })

        """append monthly and yearly statistics"""
        bdew_demand['Month'].append(MonthDict.get(month+1))
        bdew_demand['Workday\n Demand [kWh]'].append(format((workday_demand),'.2f'))
        bdew_demand['Saturday\n Demand [kWh]'].append(format((saturday_demand),'.2f'))
        bdew_demand['Sunday\n Demand [kWh]'].append(format((sunday_demand),'.2f'))

        average['Month'].append(MonthDict.get(month+1))
        average[f'{calc_type}\n Generation [kWh]'].append(format((total_generation),'.2f'))
        average[f'Workday Demand\n Covered by {calc_type}'].append(str(int(workday_demand_covered))+'%')
        average[f'Workday {calc_type}\n Used by Demand'].append(str(int(workday_generation_used))+'%')
        average[f'Saturday Demand\n Covered by {calc_type}'].append(str(int(saturday_demand_covered))+'%')
        average[f'Saturday {calc_type}\n Used by Demand'].append(str(int(saturday_generation_used))+'%')
        average[f'Sunday Demand\n Covered by {calc_type}'].append(str(int(sunday_demand_covered))+'%')
        average[f'Sunday {calc_type}\n Used by Demand'].append(str(int(sunday_generation_used))+'%')

        min['Month'].append(MonthDict.get(month+1))
        min[f'{min_name}\n {calc_type}\n Generation [kWh]'].append(format((total_min_generation),'.2f'))
        min[f'{min_name}\n Workday Demand\n Covered by {calc_type}'].append(str(int(min_workday_demand_covered))+'%')
        min[f'{min_name}\n Saturday Demand\n Covered by {calc_type}'].append(str(int(min_saturday_demand_covered))+'%')
        min[f'{min_name}\n Sunday Demand\n Covered by {calc_type}'].append(str(int(min_sunday_demand_covered))+'%')
        min[f'{min_name}\n Workday {calc_type}\n Used by Demand'].append(str(int(min_workday_generation_used))+'%')
        min[f'{min_name}\n Saturday {calc_type}\n Used by Demand'].append(str(int(min_saturday_generation_used))+'%')
        min[f'{min_name}\n Sunday {calc_type}\n Used by Demand'].append(str(int(min_sunday_generation_used))+'%')

        max['Month'].append(MonthDict.get(month+1))
        max[f'{max_name}\n {calc_type}\n Generation [kWh]'].append(format((total_max_generation),'.2f'))
        max[f'{max_name}\n Workday Demand\n Covered by {calc_type}'].append(str(int(max_workday_demand_covered))+'%')
        max[f'{max_name}\n Saturday Demand\n Covered by {calc_type}'].append(str(int(max_saturday_demand_covered))+'%')
        max[f'{max_name}\n Sunday Demand\n Covered by {calc_type}'].append(str(int(max_sunday_demand_covered))+'%')
        max[f'{max_name}\n Workday {calc_type}\n Used by Demand'].append(str(int(max_workday_generation_used))+'%')
        max[f'{max_name}\n Saturday {calc_type}\n Used by Demand'].append(str(int(max_saturday_generation_used))+'%')
        max[f'{max_name}\n Sunday {calc_type}\n Used by Demand'].append(str(int(max_sunday_generation_used))+'%')

        df_list.append(df)

    return (df_list,
            pd.DataFrame(average),
            pd.DataFrame(min),
            pd.DataFrame(max),
            pd.DataFrame(bdew_demand),
            time,
            yearly_generation,
            yearly_used_generation_only,
            yearly_used_generation_battery,
            full_hh_data)

def makedf_PV(property_type, lat, lon, annual_consumption, PV_max_power, battery_capacity_kWh, surface_tilt, surface_azimuth,start_year, end_year):
    
    generation_data = get_PV_Data(PV_max_power, start_year, end_year, lat, lon, surface_tilt, surface_azimuth)

    df_list, average, min, max, bdew_demand, time, yearly_generation, yearly_used_generation_only, yearly_used_generation_battery, full_hh_data = process_data("PV", generation_data, battery_capacity_kWh, property_type, annual_consumption)

    return (df_list,
            average,
            min,
            max,
            bdew_demand,
            time,
            yearly_generation,
            yearly_used_generation_only,
            yearly_used_generation_battery,
            full_hh_data)   


def makedf_Wind(property_type, lat, lon, annual_consumption,start_year, end_year, battery_capacity_kWh, turbine_height,land_cover_type, turbine_nominal_power = 10, turbine_rotor_diameter = 10.2, cutin_speed = 3, cutoff_speed = 25):
    
    generation_data = get_Wind_Data(start_year, end_year, lat, lon, turbine_height, land_cover_type, turbine_nominal_power, turbine_rotor_diameter, cutin_speed, cutoff_speed)

    df_list, average, min, max, bdew_demand, time, yearly_generation, yearly_used_generation_only, yearly_used_generation_battery, full_hh_data = process_data("Wind", generation_data, battery_capacity_kWh, property_type, annual_consumption)

    return (df_list,
            average,
            min,
            max,
            bdew_demand,
            time,
            yearly_generation,
            yearly_used_generation_only,
            yearly_used_generation_battery,
            full_hh_data)

# test_PV = makedf_PV(property_type = "g0", lat = 57.1437, lon = -2.0981, annual_consumption = 15000, PV_max_power= 5,  battery_capacity_kWh=5, surface_tilt = 35, surface_azimuth = 0, start_year = 2013, end_year = 2016)

# test_Wind = makedf_Wind(property_type = "g0", lat = 57.1437, lon = -2.0981, annual_consumption = 12000, start_year = 2013, end_year = 2016, battery_capacity_kWh = 5, turbine_height = 18, land_cover_type = 0.4, turbine_rotor_diameter=10.2, cutin_speed=3, cutoff_speed=25)

# average = test_Wind[1]
# min = test_Wind[2]
# max = test_Wind[3]
# bdew_demand = test_Wind[4]
# time = test_Wind[5]
# yearly_generation = test_Wind[6]
# yearly_used_generation_only = test_Wind[7]
# yearly_used_generation_battery = test_Wind[8]
# hh_data = test_Wind[9]
# sum(hh_data["GenerationEnergy_kWh"])
# sum(hh_data["ElectricityDemandAC_kWh"])
