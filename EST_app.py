import matplotlib.pyplot as plt
from EST_tidy_data import makedf
from EST_gui import get_variables
from matplotlib.widgets import Button as plotButton
import numpy as np
import pandas as pd


MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}
PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop or Barber","g5":"Bakery","g6":"Weekend Business","g7":"Mobile Phone Transmitter Station",
    "l0":"General Farm","l1":"Dairy or Livestock Farm", "l2":"Other Farm", "h0":"Household"}

property_type, lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth = get_variables()
#property_type, lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth = 'g0',56.140,-3.919,12000,8,0,35
start = 2013
end = 2016

df, average,cloudy, sunny, bdew_demand, t, yearly_gen, yearly_use = makedf(property_type, lat, lon, annual_consumption, PV_max_power, surface_tilt, surface_azimuth,start, end)
months = np.arange(0, 12, 1)
days = np.arange(0,3,1)
startmonth = 6
fig, ax = plt.subplots(figsize=(10,7))
fig.subplots_adjust(bottom=0.275)
PV = df[startmonth]['PV generation']
PV_min = df[startmonth]['PV min']
PV_max = df[startmonth]['PV max']
workday = df[startmonth]['BDEW workday']
saturday = df[startmonth]['BDEW saturday']
sunday = df[startmonth]['BDEW sunday']
ax.set_title(MonthDict[startmonth+1]+" PV Generation from a " + str(PV_max_power) + " kWp System and Demand of a "+PropertyDict[property_type])
ax.grid(alpha=0.2)
l3, = ax.plot(t, PV_max, lw=4,alpha = 0.5, color='orange')
l1, = ax.plot(t, PV, lw=6, alpha=0.8, color='orange', label = 'PV generation')
l2, = ax.plot(t, PV_min, lw=4,alpha = 0.5, color='orange')
l4, = ax.plot(t, workday, lw=4,alpha = 0.5, color='blue',label = 'Workday demand: '+str(bdew_demand['Workday\n Demand [kWh]'][startmonth])+' kWh')
l5, = ax.plot(t, saturday, lw=4,alpha = 0.5, color='blue',label = 'Saturday demand: '+str(bdew_demand['Saturday\n Demand [kWh]'][startmonth])+' kWh')
l5.set_visible(False)
l6, = ax.plot(t, sunday, lw=4,alpha = 0.5, color='blue',label = 'Sunday demand: '+str(bdew_demand['Sunday\n Demand [kWh]'][startmonth])+' kWh')
l6.set_visible(False)

ax.legend(loc = 'upper right')


plt.ylim((0,PV_max_power*2/3))
plt.xticks(np.arange(0,25,1))
stat_table = ax.table(cellText=[sunny.values[6],average.values[6],cloudy.values[6]], colLabels=average.columns, rowLabels=['Sunny','Average','Cloudy'], bbox=[0, -0.31, 1, 0.235])
stat_table.set_fontsize(8)
year_df = pd.DataFrame(index = ['a','b','c'],columns = ['Annual \nDemand: ' + str(annual_consumption)+' kWh', 'Annual PV \ngeneration: ' + (str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh'), ('Annual PV \n used: ' + str(yearly_use[0])+' ± '+str(yearly_use[1])+' kWh')])
year_table = ax.table(cellText = [[str(annual_consumption)+' kWh', (str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh'), (str(yearly_use[0])+' ± '+str(yearly_use[1])+' kWh')]],colLabels = ['Annual \nDemand','Annual PV \ngeneration','Annual PV \n used'],bbox=[0, 0.85, 0.45, 0.15])
year_table.set_fontsize(8)

class Index:
    ind = 6
    dind = 0

    def next(self, event):
        self.ind += 1
        i = self.ind % len(months)
        update1 = df[i]['PV generation']
        update2 = df[i]['PV min']
        update3 = df[i]['PV max']
        update4 = df[i]['BDEW workday']

        l1.set_ydata(update1)
        l2.set_ydata(update2)
        l3.set_ydata(update3)
        l4.set_ydata(update4)

        l4.set_label('Workday: '+str(bdew_demand['Workday\n Demand [kWh]'][i])+' kWh')
        l5.set_label('Saturday: '+str(bdew_demand['Saturday\n Demand [kWh]'][i])+' kWh')
        l6.set_label('Sunday: '+str(bdew_demand['Sunday\n Demand [kWh]'][i])+' kWh')
        
        ax.legend(loc = 'upper right')    
        ax.set_title(MonthDict[i+1]+" PV Generation from a " + str(PV_max_power) + " kWp System and Demand of a "+PropertyDict[property_type])
        #ax.table(cellText=[stats_df.values[i]], colLabels=stats_df.columns, bbox=[0, -0.14, 1, 0.075])
        [stat_table.get_celld()[(1, j)].get_text().set_text(sunny.values[i][j]) for j in range(7)]
        [stat_table.get_celld()[(2, j)].get_text().set_text(average.values[i][j]) for j in range(7)]
        [stat_table.get_celld()[(3, j)].get_text().set_text(cloudy.values[i][j]) for j in range(7)]

        plt.draw()

    def prev(self, event):
        self.ind -= 1
        i = self.ind % len(months)
        update1 = df[i]['PV generation']
        update2 = df[i]['PV min']
        update3 = df[i]['PV max']
        update4 = df[i]['BDEW workday']
        l1.set_ydata(update1)
        l2.set_ydata(update2)
        l3.set_ydata(update3)
        l4.set_ydata(update4)

        l4.set_label('Workday: '+str(bdew_demand['Workday\n Demand [kWh]'][i])+' kWh')
        l5.set_label('Saturday: '+str(bdew_demand['Saturday\n Demand [kWh]'][i])+' kWh')
        l6.set_label('Sunday: '+str(bdew_demand['Sunday\n Demand [kWh]'][i])+' kWh')

        ax.legend(loc = 'upper right')
        ax.set_title(MonthDict[i+1]+" PV Generation from a " + str(PV_max_power) + " kWp System and Demand of a "+PropertyDict[property_type])
        [stat_table.get_celld()[(1, j)].get_text().set_text(sunny.values[i][j]) for j in range(7)]
        [stat_table.get_celld()[(2, j)].get_text().set_text(average.values[i][j]) for j in range(7)]
        [stat_table.get_celld()[(3, j)].get_text().set_text(cloudy.values[i][j]) for j in range(7)]
        plt.draw()

    def workday(self,event):
        visible = not l4.get_visible()
        l4.set_visible(visible)
        plt.draw()

    def saturday(self,event):
        visible = not l5.get_visible()
        l5.set_visible(visible)        
        plt.draw()

    def sunday(self,event):
        visible = not l6.get_visible()
        l6.set_visible(visible)
        plt.draw()


callback = Index()
axprev = fig.add_axes([0.7, 0.005, 0.1, 0.065])
axnext = fig.add_axes([0.81, 0.005, 0.1, 0.065])
bxwork = fig.add_axes([0.11, 0.005, 0.1, 0.065])
bxsat = fig.add_axes([0.22, 0.005, 0.1, 0.065])
bxsun = fig.add_axes([0.33, 0.005, 0.1, 0.065])

bnext = plotButton(axnext, 'Next')
bnext.on_clicked(callback.next)
bprev = plotButton(axprev, 'Previous')
bprev.on_clicked(callback.prev)

bworkday = plotButton(bxwork,'Workday',color='cornflowerblue')
bworkday.on_clicked(callback.workday)
bsaturday = plotButton(bxsat,'Saturday',color='cornflowerblue')
bsaturday.on_clicked(callback.saturday)
bsunday = plotButton(bxsun,'Sunday',color='cornflowerblue')
bsunday.on_clicked(callback.sunday)
plt.show()

frames = [average,cloudy,sunny,bdew_demand,year_df]
start_row = 1
writer = pd.ExcelWriter(PropertyDict[property_type]+"_"+str(annual_consumption)+"kWh_"+str(PV_max_power)+"kWp.xlsx", engine='xlsxwriter')
sheet_name='Monthly Percentages'
for df in frames:  # assuming they're already DataFrames
    df.to_excel(writer, sheet_name, startrow=start_row, startcol=0, index=False)
    start_row += len(df) + 2  # add a row for the column header?
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)
writer.save()  # we only need to save to disk at the very end!