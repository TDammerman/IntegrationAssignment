import numpy as np
import Data

# time, u [m/s], theta [deg], P [MW], price [€/MWh]
TimeSeries, dates, dates_daily, dates_weekly, dates_monthly = Data.time_series_prep()

u = TimeSeries[:, 1]
Power = TimeSeries[:, 3]
Price = TimeSeries[:, 4]

months = np.array([x.month for x in dates])
idx_month = [np.where(months == month_idx)[0][0] for month_idx in range(1, 13)]
idx_month = np.append(idx_month, len(TimeSeries) - 1)

# Index of day when we start making more than avg again
start_idx = idx_month[3] + 24 * 15

u_from_zero_point = np.append(u[start_idx:], u[:start_idx + 1])
dates_from_zero_point = np.append(dates[start_idx:], dates[:start_idx + 1])
power_from_zero_point = np.append(Power[start_idx:], Power[:start_idx + 1])
price_from_zero_point = np.append(Price[start_idx:], Price[:start_idx + 1])
Stored = np.zeros(np.shape(power_from_zero_point))

# Lifetime
Investment_Lifetime = 20  # Years

# Hydrogen system
H2_max_capacity = 5_000  # MWh
H2_max_power_FC = 5  # MW
H2_max_power_El = 100  # MW
Eff_FC = 0.60  # - https://www.gminsights.com/pressrelease/fuel-cell-market
Eff_El = 0.66  # - https://iea.blob.core.windows.net/assets/9e3a3493-b9a6-4b7d-b499-7ca48e357561/The_Future_of_Hydrogen.pdf
# Costs
H2_storage_cost = 9_000  # €/MWh https://www.hydrogen.energy.gov/pdfs/19006_hydrogen_class8_long_haul_truck_targets.pdf
H2_El_cost = 800_000  # €/MW https://iea.blob.core.windows.net/assets/9e3a3493-b9a6-4b7d-b499-7ca48e357561/The_Future_of_Hydrogen.pdf
H2_FC_cost = 1_000_000  # €/MW https://www.pnnl.gov/sites/default/files/media/file/Hydrogen_Methodology.pdf
H2_OM_El = 14_480  # €/MW-year https://www.pnnl.gov/sites/default/files/media/file/Hydrogen_Methodology.pdf
H2_OM_FC = 13_430  # €/MW-year https://www.pnnl.gov/sites/default/files/media/file/Hydrogen_Methodology.pdf
H2_OM_storage = 1.0  # % of capital cost of storage system https://www.nrel.gov/docs/fy19osti/73481.pdf

# Battery system
Bat_max_capacity = 3000  # MWh
Bat_max_power = 50  # MW
Bat_discharge_rate = 0.98  # %/day https://thundersaidenergy.com/downloads/battery-degradation-what-causes-capacity-fade/#:~:text=This%20might%20be%20associated%20with,high%20discharge%20rates%20around%203C.
Bat_eff = 0.95  # - https://batterytestcentre.com.au/project/lithium-ion/
# Costs
Bat_storage_cost = 75_000  # €/MWh https://www.researchgate.net/publication/329623306_Decentralised_Energy_Market_for_Implementation_into_the_Intergrid_Concept_-_Part_2_Integrated_System/link/5c209a6992851c22a341eb51/download
Bat_power_cost = 63_000  # €/MW https://www.pnnl.gov/sites/default/files/media/file/Final%20-%20ESGC%20Cost%20Performance%20Report%2012-11-2020.pdf
Bat_OM_power = 2.5  # % of capital cost of power of the battery https://www.nrel.gov/docs/fy21osti/79236.pdf

# Arrays for parameter variation
# Hydrogen system
H2_max_capacity_arr = [2000, 2250, 2375, 2500, 2625, 2750, 3000]  # MWh
H2_max_power_FC_arr = [0, 1, 2, 3, 4, 5, 10]  # MW
H2_max_power_El_arr = [90, 95, 100, 102.5, 105, 107.5, 110, 115]  # MW

# Battery system
Bat_max_capacity_arr = [150, 200, 225, 250, 275, 300, 400]  # MWh
Bat_max_power_arr = [20, 22.5, 25, 27.5, 30, 35, 40, 45, 50, 55]  # MW


# Determining excess power from system
def excess_power():
	def power_curve():
		# From trendline in excel
		curve = np.genfromtxt("Data/PowerCurve.csv", delimiter=",")
		u_curve, P_curve = curve[1:17, 0], curve[1:17, 1]
		z = np.polyfit(u_curve, P_curve, 3)
		f = np.poly1d(z)
		return f
	
	num_turb = 70  # Number of turbines in the farm
	
	# Power curve of singular turbine, col 0, windspeed [m/s], col 1 power output [MW]
	P_curve = power_curve()
	Correction_Wake = 0.97  # [-] https://onlinelibrary-wiley-com.tudelft.idm.oclc.org/doi/am-pdf/10.1002/we.2123
	Correction_Availability = 0.8195  # [-] https://onlinelibrary-wiley-com.tudelft.idm.oclc.org/doi/10.1002/we.421#:~:text=The%20total%20annual%20WT%20downtime,(for%20the%20electrical%20system).
	P_theoretical = Correction_Availability * Correction_Wake * num_turb * P_curve(u_from_zero_point)
	P_theoretical[np.where(P_theoretical > 1000)] = 1000
	P_theoretical[np.where(u_from_zero_point < 3)] = 0
	P_theoretical[np.where(u_from_zero_point > 25.3)] = 0
	P_theoretical[np.where(P_theoretical < 0)] = 0
	
	P_excess = P_theoretical - power_from_zero_point
	P_excess[np.where(P_excess < 0)] = 0
	return P_excess, P_theoretical


Time_of_reserves = int(24 * 5)
# https://www.nerdwallet.com/article/finance/average-electric-bill-cost#:~:text=In%202021%2C%20the%20average%20U.S.,are%20more%20affordable%20than%20others.
# https://climatecommunication.yale.edu/publications/who-is-willing-to-pay-more-for-renewable-energy/#:~:text=Overall%20and%20on%20average%2C%20Americans,between%20%2431%20and%20%24200%20more.
Percentage_extra_in_price = 16.25 / 122  # [-]
Price_elec = np.average(price_from_zero_point) * (1 + Percentage_extra_in_price)  # €/MWh
Price_H2 = 2.225  # €/kg average between 2030 and 2050 https://www.pwc.com/gx/en/industries/energy-utilities-resources/future-energy/green-hydrogen-cost.html
LHV_H2 = 33.3  # kWh/kg https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
Price_H2 = Price_H2 / LHV_H2 * 10 ** 3  # €/MWh
P_excess, P_theoretical = excess_power()


def P_const(P_use_aim_avg):
	P_use_aim = P_use_aim_avg * np.ones(np.shape(dates_from_zero_point))  # MW
	return P_use_aim


P_use_aim = P_const(30)
P_sell_aim_H2 = P_const(50)

P_use_aim_arr = [P_const(2.5)] # P_const(5), P_const(7.5), P_const(10), P_const(12.5), P_const(15)]
P_sell_aim_H2_arr = [P_const(50)]
