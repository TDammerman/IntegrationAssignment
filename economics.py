from StartValues import *


def CAPEX(Hydrogen_System, Battery_System):
	H2_cost = H2_storage_cost * Hydrogen_System.max_capacity + \
			  H2_El_cost * Hydrogen_System.max_power_El + \
			  H2_FC_cost * Hydrogen_System.max_power_FC

	Bat_cost = Bat_storage_cost * (Battery_System.max_capacity / 10**6) * 10**6 + \
		Bat_power_cost * Bat_max_power
	
	CAPEX_TOT = H2_cost + Bat_cost
	
	return CAPEX_TOT


def OPEX(Hydrogen_System, Battery_System):
	H2_cost = H2_OM_storage/100 * H2_storage_cost * Hydrogen_System.max_capacity + \
		      H2_OM_El * Hydrogen_System.max_power_El + \
		      H2_OM_FC * Hydrogen_System.max_power_FC
	Bat_cost = Battery_System.max_power * Bat_power_cost * Bat_OM_power / 100
	OPEX_Year = H2_cost + Bat_cost
	OPEX_Tot = OPEX_Year * Investment_Lifetime
	
	return OPEX_Tot


def Costs(Hydrogen_System, Battery_System):
	CAPEX_costs = CAPEX(Hydrogen_System, Battery_System)
	OPEX_costs = OPEX(Hydrogen_System, Battery_System)
	Total_costs = CAPEX_costs + OPEX_costs

	return Total_costs
	
