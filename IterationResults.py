import numpy as np


def get_results():
	results = np.genfromtxt("IterationResults/iterationresults.csv", delimiter=",")
	return results


