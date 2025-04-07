import pandas as pd
import numpy as np

def scale_pv_elec_profile_kwh(pv_elec_profile: pd.DataFrame, annual_pv_kwh: float, annual_elec_kwh: float) -> pd.DataFrame:
    """
    Scale PV and electricity profiles based on annual kWh values.
    """
    # Scale values based on usage
    pv_elec_profile = pv_elec_profile.copy()
    pv_elec_profile["GenerationEnergy_kWh"] *= annual_pv_kwh / pv_elec_profile["GenerationEnergy_kWh"].sum()
    pv_elec_profile["ElectricityDemandAC_kWh"] *= annual_elec_kwh / pv_elec_profile["ElectricityDemandAC_kWh"].sum()
    
    return pv_elec_profile

def GenBatteryModel(GenDemandProfile, BatterySize_kWh=4, ChargerSize_kW=None, InverterSize_kW=None, 
                    ChargerEfficiency=0.95, InverterEfficiency=0.95, 
                    BatteryChargeUpperLimit=0.9, BatteryChargeLowerLimit=0, BatteryChargeInitial=None,
                    KeepModelData=False, ImportRate_GBP_kWh=0.16357, ExportRate_GBP_kWh=0.0399):
    
    if ChargerSize_kW is None:
        ChargerSize_kW = BatterySize_kWh
    if InverterSize_kW is None:
        InverterSize_kW = BatterySize_kWh
    if BatteryChargeInitial is None:
        BatteryChargeInitial = BatteryChargeLowerLimit
    
    GenDemandProfile = GenDemandProfile.dropna()
    TimeRange = GenDemandProfile['Time'].iloc[-1] - GenDemandProfile['Time'].iloc[0]
    TimeResolution = GenDemandProfile['Time'].iloc[1] - GenDemandProfile['Time'].iloc[0]
    
    if round(TimeRange.total_seconds() / (len(GenDemandProfile) - 1), 6) != round(TimeResolution.total_seconds(), 6):
        raise ValueError("Data not continuous - please sort and re-run")
    
    MaxChargerPower = ChargerEfficiency * ChargerSize_kW
    MaxInverterPower = InverterEfficiency * InverterSize_kW
    MaxBatteryCharge_kWh = BatterySize_kWh * BatteryChargeUpperLimit
    MinBatteryCharge_kWh = BatterySize_kWh * BatteryChargeLowerLimit
    
    InitialBatteryCharge = max(MinBatteryCharge_kWh, MaxBatteryCharge_kWh * BatteryChargeInitial)
    
    modeldf = GenDemandProfile.copy()
    modeldf['ElectricityDemandDC_kWh'] = modeldf['ElectricityDemandAC_kWh'] / InverterEfficiency
    modeldf['NetEnergyDC_kWh'] = modeldf['GenerationEnergy_kWh'] - modeldf['ElectricityDemandDC_kWh']
    modeldf['BatteryEnergyStart_kWh'] = np.nan
    modeldf['BatteryEnergyEnd_kWh'] = np.nan
    modeldf['ExportGrid_kWh'] = np.nan
    modeldf['ImportGrid_kWh'] = np.nan
    modeldf['EnergyToStorage_kWh'] = np.nan
    modeldf['PVUsed_kWh'] = np.nan
    
    for i in range(len(modeldf)):
        EnergyNeededDC_kWh = modeldf.at[i, 'NetEnergyDC_kWh']
        
        if i == 0:
            modeldf.at[i, 'BatteryEnergyStart_kWh'] = InitialBatteryCharge
        else:
            modeldf.at[i, 'BatteryEnergyStart_kWh'] = modeldf.at[i-1, 'BatteryEnergyEnd_kWh']
        
        if EnergyNeededDC_kWh < 0:
            modeldf.at[i, 'ExportGrid_kWh'] = 0
            if modeldf.at[i, 'BatteryEnergyStart_kWh'] == MinBatteryCharge_kWh:
                modeldf.at[i, 'BatteryEnergyEnd_kWh'] = MinBatteryCharge_kWh
                modeldf.at[i, 'ImportGrid_kWh'] = abs(EnergyNeededDC_kWh) * InverterEfficiency
                modeldf.at[i, 'EnergyToStorage_kWh'] = 0
                modeldf.at[i, 'PVUsed_kWh'] = modeldf.at[i, 'GenerationEnergy_kWh'] * InverterEfficiency
            else:
                battery_discharge = min(abs(EnergyNeededDC_kWh), modeldf.at[i, 'BatteryEnergyStart_kWh'] - MinBatteryCharge_kWh)
                modeldf.at[i, 'BatteryEnergyEnd_kWh'] = modeldf.at[i, 'BatteryEnergyStart_kWh'] - battery_discharge
                modeldf.at[i, 'ImportGrid_kWh'] = abs(EnergyNeededDC_kWh) * InverterEfficiency - battery_discharge * InverterEfficiency
                modeldf.at[i, 'EnergyToStorage_kWh'] = 0
                modeldf.at[i, 'PVUsed_kWh'] = modeldf.at[i, 'GenerationEnergy_kWh'] * InverterEfficiency
        else:
            modeldf.at[i, 'ImportGrid_kWh'] = 0
            if modeldf.at[i, 'BatteryEnergyStart_kWh'] < MaxBatteryCharge_kWh:
                battery_charge = min(abs(EnergyNeededDC_kWh) * ChargerEfficiency, MaxBatteryCharge_kWh - modeldf.at[i, 'BatteryEnergyStart_kWh'])
                modeldf.at[i, 'BatteryEnergyEnd_kWh'] = modeldf.at[i, 'BatteryEnergyStart_kWh'] + battery_charge
                modeldf.at[i, 'ExportGrid_kWh'] = max(0, (abs(EnergyNeededDC_kWh) - battery_charge / ChargerEfficiency) * InverterEfficiency)
                modeldf.at[i, 'EnergyToStorage_kWh'] = battery_charge
                modeldf.at[i, 'PVUsed_kWh'] = modeldf.at[i, 'ElectricityDemandAC_kWh']
            else:
                modeldf.at[i, 'BatteryEnergyEnd_kWh'] = modeldf.at[i, 'BatteryEnergyStart_kWh']
                modeldf.at[i, 'ExportGrid_kWh'] = abs(EnergyNeededDC_kWh) * InverterEfficiency
                modeldf.at[i, 'EnergyToStorage_kWh'] = 0
                modeldf.at[i, 'PVUsed_kWh'] = modeldf.at[i, 'ElectricityDemandAC_kWh']
    
    TotalEImport = modeldf['ImportGrid_kWh'].sum()
    TotalEExport = modeldf['ExportGrid_kWh'].sum()
    TotalBatteryStorageUsed = (modeldf['EnergyToStorage_kWh'].sum() - modeldf['EnergyToStorage_kWh'].iloc[-1]) * InverterEfficiency
    TotalEwithoutPV = modeldf['ElectricityDemandAC_kWh'].sum()
    TotalPVGen = modeldf['GenerationEnergy_kWh'].sum()
    TotalPVUsed_kWhDirectly = modeldf['PVUsed_kWh'].sum()
    
    YearlyCostNoPV = TotalEwithoutPV * ImportRate_GBP_kWh
    YearlyCostWithPV = TotalEImport * ImportRate_GBP_kWh
    YearlyIncome = TotalEExport * ExportRate_GBP_kWh
    CostSaving = YearlyCostNoPV - YearlyCostWithPV
    EnergySaved = TotalEwithoutPV - TotalEImport
    TotalPVSelfConsumption = TotalPVUsed_kWhDirectly + TotalBatteryStorageUsed
    TotalPVLosses = TotalPVGen - TotalPVSelfConsumption - TotalEExport
    
    output = {
        'battery_size': BatterySize_kWh,
        'elec_demand': TotalEwithoutPV,
        'pv_generation': TotalPVGen,
        'total_export': TotalEExport,
        'total_import': TotalEImport,
        'battery_storage': TotalBatteryStorageUsed,
        'cost_noPV': YearlyCostNoPV,
        'cost_PV': YearlyCostWithPV,
        'cost_saving': CostSaving,
        'income': YearlyIncome,
        'pv_self_consumption': TotalPVSelfConsumption,
        'pv_losses': TotalPVLosses,
        'pv_used_directly': TotalPVUsed_kWhDirectly,
        'energy_saved': EnergySaved
    }
    
    if KeepModelData:
        return output, modeldf
    else:
        return output
