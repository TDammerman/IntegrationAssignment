import numpy as np


def reset_results():
	empty_results = np.array([[0] * 16] * 2)
	np.savetxt("IterationResults/iterationresults.csv", empty_results, delimiter=",")


if __name__ == "__main__":
	reset_results()
