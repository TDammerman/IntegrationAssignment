import numpy as np

from Data import time_series_prep
import matplotlib.pyplot as plt


def power_curve():
    # From trendline in excel
    curve = np.genfromtxt("Data/PowerCurve.csv", delimiter=",")
    u_curve, P_curve = curve[1:17, 0], curve[1:17, 1]
    z = np.polyfit(u_curve, P_curve, 3)
    f = np.poly1d(z)
    return f


TimeSeries, dates, dates_daily, dates_weekly, dates_monthly = time_series_prep()
func = power_curve()

plt.scatter(TimeSeries[:, 1], TimeSeries[:, 3], label="Power curve from data", s=1)

curve = np.genfromtxt("Data/PowerCurve.csv", delimiter=",")
u_curve, P_curve = curve[1:, 0], 70 * curve[1:, 1]
plt.plot(u_curve, P_curve, color="green", label="Theoretical power curve")

x = np.arange(0, 30, 0.01)
Correction_Wake = 0.97  # [-] https://onlinelibrary-wiley-com.tudelft.idm.oclc.org/doi/am-pdf/10.1002/we.2123
Correction_Availability = 0.8195  # [-] https://onlinelibrary-wiley-com.tudelft.idm.oclc.org/doi/10.1002/we.421#:~:text=The%20total%20annual%20WT%20downtime,(for%20the%20electrical%20system).
y = Correction_Availability * Correction_Wake * 70 * func(x)
y[np.where(y > 1000)] = 1000
y[np.where(x < 3)] = 0
y[np.where(x > 25.3)] = 0
y[np.where(y < 0)] = 0
plt.plot(x, y, color="orange", label="Estimated power curve")

# plt.title("Power curve of the wind farm")
plt.grid(True, axis="y")
plt.legend()
plt.show()
