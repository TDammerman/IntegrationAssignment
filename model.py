from Storage import Hydrogen, Battery
import plots
import matplotlib.pyplot as plt
from StartValues import *
import economics


def hydrogen_battery_model(show_plots, P_excess, Hydrogen_system, Battery_system, P_use_aim, P_sell_aim_H2):
	"""
	:param show_plots: Bool, whether to show plots
	:param P_excess: numpy array, power available for the system, the excess power of the farm [MW]
	:param P_use_aim: numpy array, the power that is aimed to be delivered to the client at any given time [MW]
	:param Hydrogen_system: Class object, object of the hydrogen system
	:param Battery_system: Class object, object of the battery system
	:param P_use_aim: numpy array, array of the aimed power output of the farm
	:param P_sell_aim_H2: numpy array, array of the aimed power selling of the farm
	:return:
	"""
	
	Battery_filled_capacity = np.zeros(np.shape(power_from_zero_point))
	Hydrogen_filled_capacity = np.zeros(np.shape(power_from_zero_point))
	P_not_used_list = np.zeros(np.shape(power_from_zero_point))
	P_shortage_list = np.zeros(np.shape(power_from_zero_point))
	Power_output = np.zeros(np.shape(power_from_zero_point))
	P_sell_H2_list = np.zeros(np.shape(power_from_zero_point))
	Revenue_elec_list = np.zeros(np.shape(power_from_zero_point))
	Revenue_H2_list = np.zeros(np.shape(power_from_zero_point))
	Revenue_tot_list = np.zeros(np.shape(power_from_zero_point))
	P_used_list = np.zeros(np.shape(power_from_zero_point))
	
	P_available_list = P_excess - P_use_aim
	
	for i in range(len(P_excess)):
		# Positive if we can store, negative if we need to take out of storage
		# If statement to take into account we need to have something in storage for the next year
		if i + Time_of_reserves < len(P_use_aim):
			E_reserve = np.sum(P_use_aim[i:i + Time_of_reserves])
		else:
			days_in_next_year = Time_of_reserves - (len(P_use_aim) - i)
			E_reserve = np.sum(P_use_aim[i:]) + np.sum(P_use_aim[:days_in_next_year])
		
		P_residual, P_stored_bat = Battery_system.store(P_available_list[i], E_reserve)
		
		if P_residual != 0:
			P_not_used, P_shortage, P_stored_H2, P_sold_H2 = Hydrogen_system.store(P_residual, E_reserve,
			                                                                       Battery_system, P_sell_aim_H2[i])
		else:
			P_not_used, P_shortage, P_stored_H2, P_sold_H2 = 0, 0, 0, 0
		
		P_output = P_use_aim[i] + P_shortage
		Revenue_elec = Investment_Lifetime * P_output * Price_elec
		Revenue_H2 = Investment_Lifetime * P_sold_H2 * Price_H2
		Revenue_tot = Revenue_elec + Revenue_H2
		
		Battery_filled_capacity[i] = Battery_system.filled_capacity
		Hydrogen_filled_capacity[i] = Hydrogen_system.filled_capacity
		P_not_used_list[i] = P_not_used
		P_shortage_list[i] = P_shortage
		Power_output[i] = P_output
		P_sell_H2_list[i] = P_sold_H2
		Revenue_elec_list[i] = Revenue_elec
		Revenue_H2_list[i] = Revenue_H2
		Revenue_tot_list[i] = Revenue_tot
		P_used_list[i] = P_stored_bat + P_stored_H2 + P_sold_H2
	
	investment_cost = economics.Costs(Hydrogen_system, Battery_system) / 10 ** 6
	P_total_normal = np.sum(P_theoretical)
	P_total_curtail = np.sum(power_from_zero_point)
	E_not_used = np.sum(P_not_used_list)
	Revenue_tot = np.sum(Revenue_tot_list) / 10 ** 6
	P_Reliability = len(np.where(Power_output == P_use_aim)[0]) / len(Power_output) * 100
	H2_Reliability = len(np.where(P_sell_H2_list == P_sell_aim_H2)[0]) / len(P_sell_H2_list) * 100
	Profit = Revenue_tot - investment_cost
	Percentage_used = np.sum(P_used_list) / P_total_curtail * 100
	
	if show_plots:
		plots.power_plot(dates_from_zero_point, Power_output, P_sell_H2_list)
		plots.battery_hydrogen_plot(dates_from_zero_point, Battery_filled_capacity, Hydrogen_filled_capacity)
		plots.revenue_plot(dates_from_zero_point, Revenue_elec_list, Revenue_H2_list, Revenue_tot_list)
		print(f"Total energy:      {'{:10.2f}'.format(P_total_normal)} [MWh] \n"
		      f"Total used:        {'{:10.2f}'.format(np.sum(P_used_list))} [MWh] \n"
		      f"Percentage used:   {'{:10.2f}'.format(Percentage_used)} [%] \n"
		      f"Power Reliability: {'{:10.2f}'.format(P_Reliability)} [%] \n"
		      f"H2 Reliability     {'{:10.2f}'.format(H2_Reliability)} [%] \n"
		      f"Maximum profit:    {'{:10.2f}'.format(Profit)} [M$] \n"
		      f"Total revenue:     {'{:10.2f}'.format(Revenue_tot)} [M$] \n"
		      f"Investment cost:   {'{:10.2f}'.format(investment_cost)} [M$] \n"
		      f"ROI:               {'{:10.2f}'.format(Revenue_tot/investment_cost*100)} [%]")
	# E_tot, E_used, Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue, Investment_Cost
	return P_total_normal, np.sum( P_used_list), Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue_tot, \
		investment_cost


def multi_processing_model(arr):
	H2_max_capacity, Bat_max_capacity, Bat_max_power, \
		H2_max_power_El, H2_max_power_FC, P_use_aim, P_sell_aim_H2 = arr
	
	Hydrogen_system = Hydrogen(H2_max_capacity, H2_max_power_FC, H2_max_power_El, Eff_FC, Eff_El)
	Battery_system = Battery(Bat_max_capacity, Bat_max_power, Bat_discharge_rate, Bat_eff)
	
	E_tot, E_used, Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue, Investment_Cost = hydrogen_battery_model(
		False, P_excess, Hydrogen_system, Battery_system, P_use_aim, P_sell_aim_H2)
	Results = [H2_max_capacity, Bat_max_capacity, Bat_max_power, H2_max_power_El, H2_max_power_FC, P_use_aim[0],
	           P_sell_aim_H2[0], Investment_Lifetime,
	           E_tot, E_used, Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue, Investment_Cost]
	
	return Results


if __name__ == "__main__":
	Hydrogen_system = Hydrogen(H2_max_capacity, H2_max_power_FC, H2_max_power_El, Eff_FC, Eff_El)
	Battery_system = Battery(Bat_max_capacity, Bat_max_power, Bat_discharge_rate, Bat_eff)
	
	E_tot, E_used, Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue, Investment_Cost = hydrogen_battery_model(
		True, P_excess, Hydrogen_system, Battery_system, P_use_aim, P_sell_aim_H2)

	print(f"Revenue lifetime:  {Revenue} [M€]")
	print(f"Investment cost:   {Investment_Cost} [M€]")
	print(f"Profit:            {Profit} [M€]")
	
	plt.show()
