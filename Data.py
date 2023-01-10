import datetime

import numpy as np
import matplotlib.pyplot as plt
import xlrd


def time_series_prep():
	# time, u [m/s], theta [deg], P [MW], price [€/MWh]
	TimeSeries = np.genfromtxt("Data/TimeSeries.csv", autostrip=True, delimiter=",", skip_header=True)
	
	dates = [datetime.datetime(*xlrd.xldate_as_tuple(x, 0)) for x in TimeSeries[:, 0]]
	
	dates_daily = [dates[i] for i in range(0, len(TimeSeries), 24)]
	dates_weekly = [dates[i] for i in range(0, len(TimeSeries), 24 * 7)]
	
	months = np.array([x.month for x in dates])
	idx_month = [np.where(months == month_idx)[0][0] for month_idx in range(1, 13)]
	idx_month = np.append(idx_month, len(TimeSeries) - 1)
	dates_monthly = [dates[idx] for idx in idx_month]
	
	return TimeSeries, dates, dates_daily, dates_weekly, dates_monthly


def time_series():
	TimeSeries, dates, dates_daily, dates_weekly, dates_monthly = time_series_prep()
	
	power_subplot = time_series_plot.add_subplot(111)
	power_subplot.set_xlabel("Date")
	power_subplot.set_ylabel("Power [MW]")
	power_subplot.set_title("Power")
	
	# Hour plot
	power_subplot.plot(dates, TimeSeries[:, 3])
	
	# Day plot
	average_power_daily = [np.average(TimeSeries[i:i+25, 3]) for i in range(0, len(TimeSeries), 24)]
	power_subplot.plot(dates_daily, average_power_daily)
	
	# Week plot
	average_power_weekly = [np.average(TimeSeries[i:i+8, 3]) for i in range(0, len(TimeSeries), 24*7)]
	power_subplot.plot(dates_weekly, average_power_weekly)
	
	# Month plot
	months = np.array([x.month for x in dates])
	idx_month = [np.where(months == month_idx)[0][0] for month_idx in range(1, 13)]
	idx_month = np.append(idx_month, len(TimeSeries) - 1)
	average_power_monthly = [np.average(TimeSeries[idx_month[i]:idx_month[i+1], 3]) for i in range(12)]
	power_subplot.plot(dates_monthly[:-1], average_power_monthly)
	

def power_curve():
	# u [m/s], P [MW]
	PowerCurve = np.genfromtxt("Data/PowerCurve.csv", autostrip=True, delimiter=",", skip_header=True)

	subplot = power_curve_plot.add_subplot(111)
	subplot.plot(PowerCurve[:, 0], PowerCurve[:, 1])
	subplot.set_xlabel("u [m/s]")
	subplot.set_ylabel("Power [MW]")
	subplot.set_title("Power Curve")


def wind_turbines():
	# idx, lat [deg], lon [deg], easting [m], northing [m]
	WindTurbines = np.genfromtxt("Data/WindTurbines.csv", autostrip=True, delimiter=",", skip_header=True)

	subplot = wind_turbine_plot.add_subplot(111)
	subplot.scatter(WindTurbines[:, 3], WindTurbines[:, 4])
	subplot.set_xlabel("Easting [m]")
	subplot.set_ylabel("Northing [m]")
	subplot.set_title("Farm Layout")
	

if __name__ == "__main__":
	wind_turbine_plot = plt.figure()
	power_curve_plot = plt.figure()
	time_series_plot = plt.figure()
	
	time_series()
	power_curve()
	wind_turbines()
	
	plt.show()
	