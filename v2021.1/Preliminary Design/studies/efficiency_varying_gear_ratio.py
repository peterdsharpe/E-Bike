import os, sys
from pathlib import Path

this_dir = Path(__file__).parent
sys.path.insert(0, str(this_dir.parent))
from bike import Bike
import aerosandbox.numpy as np
from aerosandbox.tools.pretty_plots import plt, show_plot, set_ticks
from scipy import optimize

speed = 15 / 2.24

fig, ax = plt.subplots()
t = np.linspace(0, 10, 500)

gear_ratios = np.geomspace(
    0.020 / 0.700,
    0.700 / 0.700,
    300
)


def get_efficiency(gear_ratio):
    bike = Bike(gear_ratio=gear_ratio)

    throttle = optimize.minimize(
        fun=lambda x: (bike.performance(speed=speed, throttle_state=x)['net acceleration']) ** 2,
        x0=np.array([1]),
        bounds=[(0, 1)],
    ).x

    perf = bike.performance(speed=speed, throttle_state=throttle)

    if np.abs(perf['net acceleration']) <= 1e-6:
        return perf['efficiency']
    else:
        return np.NaN


eff = np.array([
    get_efficiency(gear_ratio)
    for gear_ratio in gear_ratios
])

plt.plot(gear_ratios, eff)
plt.xlim(gear_ratios[0], gear_ratios[-1])
plt.ylim(0, 1)
# plt.xscale('log')
set_ticks(
    x_major=0.1, x_minor=0.025,
    y_major=0.1, y_minor=0.025
)
show_plot(
    "Electric Bike: Gear Ratios",
    xlabel="Gear Ratio",
    ylabel="Efficiency"
)
