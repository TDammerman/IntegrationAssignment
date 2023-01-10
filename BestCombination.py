import time
from matplotlib import pyplot as plt

import IterationResults
from StartValues import *
from Storage import Hydrogen, Battery
from model import hydrogen_battery_model


def get_optimum_combination(results, t_start=None):
	print(f"Finding optimum combination. \n"
	      f"Considering {len(results)} combinations.\n")
	
	# Sort on profit, the highest profit is at index 0
	sorted_results = results[results[:, 13].argsort()][::-1]
	
	P_reliability_min = 90  # %
	P_outtake_min = 10  # %
	
	for i, P_reliability in enumerate(sorted_results[:, 11]):
		if P_reliability >= P_reliability_min and sorted_results[i, 10] >= P_outtake_min:
			idx_optimum = i
			if t_start is not None:
				print(f"Runtime:           {'{:10.2f}'.format(time.time() - t_start)} [s]\n")
			print(idx_optimum)
			print(f"Hydrogen capacity: {'{:10.2f}'.format(sorted_results[idx_optimum, 0])} [MWh] \n"
			      f"Battery capacity:  {'{:10.2f}'.format(sorted_results[idx_optimum, 1])} [MWh] \n"
			      f"Battery max power: {'{:10.2f}'.format(sorted_results[idx_optimum, 2])} [MW] \n"
			      f"El max power:      {'{:10.2f}'.format(sorted_results[idx_optimum, 3])} [MW] \n"
			      f"FC max power:      {'{:10.2f}'.format(sorted_results[idx_optimum, 4])} [MW] \n"
			      f"Power use aim      {'{:10.2f}'.format(sorted_results[idx_optimum, 5])} [MW] \n"
			      f"Power sell H2 aim: {'{:10.2f}'.format(sorted_results[idx_optimum, 6])} [MW] \n"
			      f"Lifetime:          {'{:10.2f}'.format(sorted_results[idx_optimum, 7])} [MW] \n")
			
			Hydrogen_system = Hydrogen(sorted_results[idx_optimum, 0], sorted_results[idx_optimum, 4],
			                           sorted_results[idx_optimum, 3], Eff_FC, Eff_El)
			Battery_system = Battery(sorted_results[idx_optimum, 1], sorted_results[idx_optimum, 2],
			                         Bat_discharge_rate,
			                         Bat_eff)
			hydrogen_battery_model(True, P_excess, Hydrogen_system, Battery_system,
			                       P_const(sorted_results[idx_optimum, 5]), P_const(sorted_results[idx_optimum, 6]))
			plt.show()
			break
	else:
		print(
			f"No options with a power reliability of {P_reliability_min}% and more than {P_outtake_min}% power outtake have been found.")
		

if __name__ == "__main__":
	Results = IterationResults.get_results()
	get_optimum_combination(Results)
	