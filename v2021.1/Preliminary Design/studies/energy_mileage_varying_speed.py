import os, sys
from pathlib import Path

this_dir = Path(__file__).parent
sys.path.insert(0, str(this_dir.parent))
from bike import Bike
import aerosandbox.numpy as np
from aerosandbox.tools.pretty_plots import plt, show_plot, set_ticks
from scipy import optimize

fig, ax = plt.subplots()
speeds = np.linspace(0, 30, 500)


def get_mileage(speed):
    bike = Bike()
    try:
        perf = bike.steady_state_performance(
            speed=speed,
        )
    except ValueError:
        return np.NaN

    motor = perf['motor state']
    power = motor['voltage'] * motor['current']

    return power / speed


mileage = np.array([
    get_mileage(speed)
    for speed in speeds
])  # J/m

mileage_Wh_per_mile = mileage / 3600 * 1000 * 1.609

plt.plot(speeds * 2.24, mileage_Wh_per_mile)
plt.xlim(left=0)
plt.ylim(bottom=0, top=50)
set_ticks(
    x_major=5, x_minor=1,
    y_major=5, y_minor=1
)
show_plot(
    f"Electric Bike: Mileage vs. Speed",
    xlabel="Speed [mph]",
    ylabel=f"Energy Mileage [Wh per mile]"
)
