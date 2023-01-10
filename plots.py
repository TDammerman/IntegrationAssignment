import matplotlib.pyplot as plt
from StartValues import *


def reorder_to_year(array):
	array = np.array(array)
	array_return = np.empty(np.shape(array), dtype="object")
	array_return[:start_idx+1] = array[len(array)-start_idx-1:]
	array_return[start_idx+1:] = array[:len(array)-start_idx-1]
	return array_return
	
	
def battery_hydrogen_plot(x, battery_filled_storage, hydrogen_filled_storage):
	x = reorder_to_year(x)
	battery_filled_storage = reorder_to_year(battery_filled_storage)
	hydrogen_filled_storage = reorder_to_year(hydrogen_filled_storage)
	
	fig, ax = plt.subplots(2, 1, constrained_layout=True)
	
	ax[0].plot(x, battery_filled_storage, label="Battery")
	ax[0].set_title("Battery filled capacity")
	ax[0].set_xlabel("Date")
	ax[0].set_ylabel("Storage [MWh]")
	ax[0].legend()
	
	ax[1].plot(x, hydrogen_filled_storage, label="Hydrogen")
	ax[1].set_title("Hydrogen filled capacity")
	ax[1].set_xlabel("Date")
	ax[1].set_ylabel("Storage [MWh]")
	ax[1].legend()


def power_plot(x, power_output, power_sell_H2):
	x = reorder_to_year(x)
	power_output = reorder_to_year(power_output)
	power_sell_H2 = reorder_to_year(power_sell_H2)
	
	fig, ax = plt.subplots(2, 1, constrained_layout=True)
	
	ax[0].scatter(x, power_output, label="Output [MW]", s=3)
	ax[0].set_title("Power of Electricity sold")
	ax[0].set_xlabel("Date")
	ax[0].set_ylabel("Power [MW]")
	ax[0].legend()
	
	ax[1].scatter(x, power_sell_H2, label="H2 sold [MW]", s=3)
	ax[1].set_title("Power of Hydrogen sold")
	ax[1].set_xlabel("Date")
	ax[1].set_ylabel("Power [MW]")
	ax[1].legend()


def revenue_plot(x, revenue_elec, revenue_H2, revenue_tot):
	x = reorder_to_year(x)
	revenue_elec = reorder_to_year(revenue_elec)
	revenue_H2 = reorder_to_year(revenue_H2)
	
	fig, ax = plt.subplots(1, 1, constrained_layout=True)
	
	ax.scatter(x, revenue_elec, label="Revenue electricity [€]", color=(0.5, 1, 0.5), s=3)
	ax.scatter(x, revenue_H2, label="Revenue hydrogen [€]", color=(0.5, 0.5, 1), s=3)
	ax.set_title("Revenue")
	ax.set_xlabel("Date")
	ax.set_ylabel("Revenue [€]")
	
	ax.legend()
	