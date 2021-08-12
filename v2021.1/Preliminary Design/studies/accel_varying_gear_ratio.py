import os, sys
from pathlib import Path

this_dir = Path(__file__).parent
sys.path.insert(0, str(this_dir.parent))
from bike import Bike
import aerosandbox.numpy as np
from aerosandbox.tools.pretty_plots import plt, show_plot, set_ticks

fig, ax = plt.subplots()
t = np.linspace(0, 10, 500)

gear_ratios = np.geomspace(
    0.020 / 0.700,
    0.700 / 0.700,
    10
)

colors = plt.cm.get_cmap('rainbow')(np.linspace(0, 1, len(gear_ratios)))

for i, gear_ratio in enumerate(gear_ratios):
    pos, vel = Bike(gear_ratio=gear_ratio).simulate(t)
    plt.plot(t, vel * 2.24,
             label=f"{gear_ratio * 0.700 * 1e3:.0f}",
             color=colors[i],
             )
set_ticks(1, 0.5, 5, 1)
show_plot(
    "Electric Bike: Gear Ratios",
    xlabel="Time [s]",
    ylabel="Speed [mph]"
)
