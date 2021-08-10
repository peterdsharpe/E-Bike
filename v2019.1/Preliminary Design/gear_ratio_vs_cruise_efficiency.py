import numpy as np
import sympy as sp
from scipy import integrate
import matplotlib.pyplot as plt
import pint

u = pint.UnitRegistry()
from motor import *


# Design Vars
cells = 6  # lipo cells
motor = Motor(
    kv=110,  # rpm/volt
    resistance=0.107,  # ohms
    no_load_current=0.7,  # amps
)
max_current = 40 * u.amps
gear_ratio = 5.5
tire_diam = 508 * u.mm
battery_capacity = 12 * u.amps * u.hours
total_mass = 170 * u.pound

# Other constants
design_hill_grade = 0  # percent
air_density = 1.225 * u.kg / u.m ** 3
rolling_resistance_coeff = 0.008
CdA = 0.4 * u.meter ** 2
gravity = 9.81 * u.m / u.s ** 2

def efficiency_at_speed(gear_ratio, speed):
    # Derived Vars
    max_voltage = cells * 3.7 * u.volts
    design_hill_angle = np.arctan(design_hill_grade / 100) * u.radians

    # Force calculation
    force_drag = (0.5 * air_density * speed ** 2 * CdA).to(u.newtons)
    force_rolling_resistance = (total_mass * rolling_resistance_coeff * gravity).to(u.newtons)
    force_hill = ((total_mass * gravity * np.sin(design_hill_angle))).to(u.newtons)
    total_resistance = force_drag + force_rolling_resistance + force_hill

    # Motor calcs
    tire_speed = (speed / (tire_diam / 2)).to(u.radians / u.seconds)
    tire_torque = total_resistance * (tire_diam / 2)
    motor_speed = tire_speed * gear_ratio
    motor_torque = tire_torque / gear_ratio

    voltage, current, rpm, torque = motor.performance(
        rpm=motor_speed.to(u.rpm).magnitude,
        torque=motor_torque.to(u.newton*u.meters).magnitude
    )

    # Dimensionalize everything
    voltage = voltage * u.volts
    current = current * u.amps
    rpm = rpm * u.rpm
    torque = torque * u.newton * u.meters

    return (rpm.to(u.radians / u.sec)*torque) / (voltage*current)


gear_ratios = np.linspace(5,13)
cruise_speeds = np.linspace(1,30) * u.mph

fig, ax = plt.subplots()
plt.xlabel("Gear Ratio")
plt.ylabel("Speed (mph)")
plt.title("Bike Cruise Efficiency on a %.2f%% Hill" % design_hill_grade)
plt.grid(True)

efficiencies = np.zeros(shape=
                        (len(gear_ratios), len(cruise_speeds))
                             )

for i in range(len(gear_ratios)):
    for j in range(len(cruise_speeds)):
        efficiencies[i,j]=efficiency_at_speed(gear_ratios[i], cruise_speeds[j])

cs = plt.contour(gear_ratios,cruise_speeds,efficiencies*100, levels = np.arange(0,100,5))
ax.clabel(cs)

# plt.xlim((0,t_max))
# plt.ylim((0,30))
plt.legend()
plt.show()

# plt.figure()
#
# plt.subplot(2,2,1)
# plt.title("Speed vs. Voltage")
# plt.xlabel("Speed (mph)")
# plt.ylabel("Voltage")
# plt.plot(speeds,voltages)
#
# plt.subplot(2,2,2)
# plt.title("Speed vs. Current")
# plt.xlabel("Speed (mph)")
# plt.ylabel("Current (amps)")
# plt.plot(speeds,currents)
#
# plt.subplot(2,2,3)
# plt.title("Speed vs. Power")
# plt.xlabel("Speed (mph)")
# plt.ylabel("Power (watts)")
# plt.plot(speeds,voltages*currents)
# plt.plot(speeds,motor_speeds * motor_torques)
#
# plt.show()
