import os, sys
from pathlib import Path

this_dir = Path(__file__).parent
sys.path.insert(0, str(this_dir.parent))
from bike import Bike
import aerosandbox.numpy as np
from aerosandbox.tools.pretty_plots import plt, show_plot, set_ticks
from scipy import optimize

speed = 24 / 2.24

fig, ax = plt.subplots()
t = np.linspace(0, 10, 500)

gear_ratios = np.geomspace(
    0.020 / 0.700,
    0.700 / 0.700,
    300
)


def get_efficiency(gear_ratio):
    bike = Bike(gear_ratio=gear_ratio)
    try:
        perf = bike.steady_state_performance(
            speed=speed
        )
    except ValueError:
        return np.NaN

    return perf['motor state']['efficiency']


eff = np.array([
    get_efficiency(gear_ratio)
    for gear_ratio in gear_ratios
])

plt.plot(gear_ratios, eff * 100)
plt.xlim(gear_ratios[0], gear_ratios[-1])
plt.ylim(0, 100)
# plt.xscale('log')
set_ticks(
    x_major=0.1, x_minor=0.025,
    y_major=10, y_minor=2.5
)
show_plot(
    f"Electric Bike: Gear Ratios at {speed * 2.24:.0f} mph",
    xlabel="Gear Ratio",
    ylabel=f"Efficiency [%]"
)
