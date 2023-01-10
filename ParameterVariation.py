import time
import itertools as it
from multiprocessing import Pool
from multiprocessing import freeze_support

import IterationResults
from BestCombination import get_optimum_combination
from model import multi_processing_model
from StartValues import *


def combinations_multi_processing(show_plots):
	def run_multiprocessing(func, i, n_processors):
		with Pool(processes=n_processors) as pool:
			return pool.map(func, i)
	
	def get_new_combinations():
		print("Determining the new combinations. \n")
		
		previous_parameters = previous_results[:, :8]
		
		combinations_array = np.array(list(combinations), dtype="object")
		formatted_combinations_array = np.array(combinations_array, dtype="object")
		formatted_combinations_array = np.append(formatted_combinations_array, Investment_Lifetime * np.ones((len(formatted_combinations_array[:, 0]), 1)), axis=1)
		
		for i in range(len(formatted_combinations_array)):
			formatted_combinations_array[i, 5] = formatted_combinations_array[i, 5][0]
			formatted_combinations_array[i, 6] = formatted_combinations_array[i, 6][0]
		
		new_combinations_bool = [not (previous_parameters == list(combi)).all(axis=1).any() for combi in formatted_combinations_array]
		new_combinations = combinations_array[new_combinations_bool]
		
		num_new_combinations = len(new_combinations)
		new_combinations = iter(new_combinations)
		
		return new_combinations, num_new_combinations
	
	t_start = time.time()
	
	num_combinations = len(H2_max_capacity_arr) * len(Bat_max_capacity_arr) * len(Bat_max_power_arr) * \
	                   len(H2_max_power_El_arr) * len(H2_max_power_FC_arr) * len(P_use_aim_arr) * len(P_sell_aim_H2_arr)
	
	print(f"Number of combinations considered: {num_combinations} \n")
	
	combinations = it.product(H2_max_capacity_arr, Bat_max_capacity_arr, Bat_max_power_arr, H2_max_power_El_arr,
	                          H2_max_power_FC_arr, P_use_aim_arr, P_sell_aim_H2_arr)
	
	previous_results = IterationResults.get_results()
	
	new_combinations, num_new_combinations = get_new_combinations()
	
	new_combinations = iter(new_combinations)
	
	# In the form:
	# H2 capacity, Bat capacity, Bat power, El power, FC power, P aim, H2 aim, Investment lifetime,
	# E_tot, E_used, Percentage_used, P_Reliability, H2_Reliability, Profit, Revenue, Investment_Cost
	print(f"Running the model over all new combinations. \n\n"
	      f"Number of combinations considered: {num_new_combinations} \n"
	      f"Expected time to run:              {round(num_new_combinations * 139 / 7776)} [s] or {round(num_new_combinations * 139 / 7776 / 60)} [min] \n"
	      f"Finished around:                   {time.ctime(t_start + num_new_combinations * 139 / 7776)}\n")
	Results = run_multiprocessing(multi_processing_model, new_combinations, 8)
	Results = np.array(Results)
	Results = np.append(previous_results, Results, axis=0)
	
	np.savetxt("IterationResults/iterationresults.csv", Results, delimiter=",")
	
	get_optimum_combination(Results, t_start)
