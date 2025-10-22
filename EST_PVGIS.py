from pvlib_parse import get_pvgis_hourly
import pandas as pd
import numpy as np
from EST_BDEW import yearly_BDEW
from PVBatteryModelFunctions import GenBatteryModel
import GenericWindTurbinePowerCurve as GWTPC

def get_PV_Data(
        max_power,
        startyear,
        endyear,
        latitude,
        longitude,
        surface_tilt,
        surface_azimuth,
        pvtechchoice="crystSi",
        mountingplace="free"
        ):
    
    data, meta, inputs = get_pvgis_hourly(
        latitude,
        longitude,
        start=startyear,
        end=endyear,
        pvcalculation=True,
        peakpower=max_power,
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        pvtechchoice=pvtechchoice,
        mountingplace=mountingplace,
    )
    
    return startyear, endyear, data

def get_Wind_Data(
        startyear,
        endyear,
        latitude,
        longitude,
        turbine_height,
        land_cover_type,
        turbine_nominal_power = 10,
        turbine_rotor_diameter = 10.2,
        cutin_speed = 3,
        cutoff_speed = 25
        ):
    
    data, meta, inputs = get_pvgis_hourly(
        latitude,
        longitude,
        start=startyear,
        end=endyear
    )
    
    #Correct wind speed to height of turbine : https://wind-data.ch/tools/profile.php?lng=en
    data["wind_speed"] = data["wind_speed"] * np.log(turbine_height/land_cover_type) / np.log(10/land_cover_type)

    data["P"] = GWTPC.GenericWindTurbinePowerCurve(data["wind_speed"],
                                                           Pnom=turbine_nominal_power,
                                                           Drotor=turbine_rotor_diameter,
                                                           Vcutin=cutin_speed,
                                                           Vcutoff=cutoff_speed)*1000
    return startyear, endyear, data
    
    


def CalculateBatterySavings(
    generation_data,
    battery_size_kWh,
    property_type,
    yearly_consumption
):
    
    startyear, endyear, data = generation_data    
    
    numyears = endyear - startyear + 1

    years = np.arange(startyear, endyear + 1, 1).tolist()
    all_years_daily_average = []
    all_years_daily_error = []
    yearly_gen_pv_only = []
    yearly_use_pv_only = []
    yearly_use_battery = []
    for year in years:

        """MONTHLY ANALYSIS"""
        monthsyear = []
        groupyear = data["P"][str(year)].groupby(pd.Grouper(freq="ME"))
        for date, group in groupyear:
            monthsyear.append(np.array(group.to_numpy()))

        numdaysofmonth = [len(monthsyear[i]) / (24) for i in range(len(monthsyear))]
        one_year_average = [
            np.mean(np.hsplit(np.array(monthsyear[i]), numdaysofmonth[i]), axis=0)
            for i in range(len(numdaysofmonth))
        ]
        all_years_daily_average.append(one_year_average)
        one_year_error = [
            np.std(
                np.hsplit(np.array(monthsyear[i]), numdaysofmonth[i]), ddof=1, axis=0
            )
            / np.sqrt(numdaysofmonth[i])
            for i in range(len(numdaysofmonth))
        ]
        all_years_daily_error.append(one_year_error)

        """YEARLY ANALYSIS"""
        yearly_demand = (
            yearly_BDEW(property_type, year, yearly_consumption)
            .resample(rule="h")
            .sum()
            # / 4
        )
        yearly_demand = yearly_demand[property_type]
        yearly_pv = data["P"][str(year)] / 1000
        
        # Add logic for pv battery model
        pv_profile = yearly_pv.reset_index().rename(columns = {
            "time":"Time",
            "P":"GenerationEnergy_kWh"})
        
        demand_profile = yearly_demand.reset_index().rename(columns = {"index":"Time", property_type: "ElectricityDemandAC_kWh"})
        
        pv_profile['Time'] = pd.to_datetime(pv_profile['Time'], utc=True).dt.floor('h')
        demand_profile['Time'] = pd.to_datetime(demand_profile['Time'], utc=True).dt.floor('h')

        
        combined_profile = pd.merge(pv_profile, demand_profile, on = "Time")
        
        if battery_size_kWh > 0:
            run_battery_model, full_hh_data = GenBatteryModel(combined_profile, BatterySize_kWh = battery_size_kWh, KeepModelData=True, InverterEfficiency = 1)
            yearly_use_battery.append(run_battery_model["pv_self_consumption"].astype("int"))
        
        intersection = np.amin([yearly_demand, yearly_pv], axis=0)
        yearly_gen_pv_only.append(np.sum(yearly_pv).astype(int))
        yearly_use_pv_only.append(np.sum(intersection).astype(int))

    daily_average = np.mean(all_years_daily_average, axis=0)
    daily_error = np.sqrt(np.sum(np.square(all_years_daily_error), axis=0)) / numyears
    
    gen_error = np.nan#np.std(np.array(yearly_gen_pv_only), ddof=1) / np.sqrt(len(yearly_gen_pv_only))
    use_error = np.nan#np.std(np.array(yearly_use_pv_only), ddof=1) / np.sqrt(len(yearly_use_pv_only))
    
    generation_total_mean = int(np.mean(yearly_gen_pv_only))
    generation_total_ci = np.nan#int(1.96*gen_error)
    pv_only_self_cons_mean = int(np.mean(yearly_use_pv_only))
    pv_only_self_cons_ci = np.nan#int(1.96*use_error)
    
    if battery_size_kWh > 0:        
        batt_error = np.nan#np.std(np.array(yearly_use_battery), ddof=1) / np.sqrt(len(yearly_use_battery))
        pv_battery_self_cons_mean = int(np.mean(yearly_use_battery))
        pv_battery_self_cons_ci = np.nan#int(1.96*batt_error)
    else:
        batt_error = np.nan
        pv_battery_self_cons_mean = np.nan
        pv_battery_self_cons_ci = np.nan
        full_hh_data = pd.DataFrame([])

    return (
        daily_average / 1000,
        daily_error / 1000,
        (generation_total_mean, generation_total_ci),
        (pv_only_self_cons_mean, pv_only_self_cons_ci),
        (pv_battery_self_cons_mean, pv_battery_self_cons_ci),
        full_hh_data
    )  # convert into kWh


# yearly_demand = (
#     yearly_BDEW("g0", 2013, 5000)
#     .resample(rule="h")
#     .sum()
# )
# yearly_demand = sum(yearly_demand["g0"])
