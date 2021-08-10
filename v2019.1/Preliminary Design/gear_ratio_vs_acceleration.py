import numpy as np
import sympy as sp
from scipy import integrate
import matplotlib.pyplot as plt
import pint

u = pint.UnitRegistry()
from motor import *

# Design Vars
cells = 12  # lipo cells
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

def acceleration_at_speed(gear_ratio, speed):
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
    motor_speed = tire_speed * gear_ratio

    voltage, current, rpm, torque = motor.performance(
        rpm=motor_speed.to(u.rpm).magnitude,
        voltage=max_voltage.to(u.volts).magnitude
    )
    if current > max_current.to(u.amps).magnitude:
        voltage, current, rpm, torque = motor.performance(
            rpm=motor_speed.to(u.rpm).magnitude,
            current=max_current.to(u.amps).magnitude
        )

    # Dimensionalize everything
    voltage = voltage * u.volts
    current = current * u.amps
    rpm = rpm * u.rpm
    torque = torque * u.newton * u.meters

    # Find net force
    tire_torque = torque * gear_ratio
    tire_force = tire_torque / (tire_diam / 2)

    net_force = tire_force - total_resistance
    net_accel = (net_force / total_mass).to(u.meters / u.seconds ** 2)

    return net_accel


gear_ratios = np.arange(5,13,1)
t_max = 15
n_timesteps = 50

plt.figure()
plt.xlabel("Time (seconds)")
plt.ylabel("Speed (mph)")
plt.title("Bike Acceleration Profiles on a %.2f%% Hill" % design_hill_grade)
plt.grid(True)

for gear_ratio in gear_ratios:
    def dvdt(t, v):
        v_dimensional = v * u.meters / u.seconds
        accel = acceleration_at_speed(gear_ratio, v_dimensional)
        accel_dimensionless = accel.to(u.meters / u.seconds ** 2).magnitude
        return np.array((accel_dimensionless))

    results = integrate.solve_ivp(dvdt, t_span=(0, t_max), y0=np.array([0]), t_eval=np.linspace(0,t_max,n_timesteps))
    t = results.t
    v = results.y[0,:] * u.meters / u.seconds
    v_mph = v.to(u.mph)


    plt.plot(t,v_mph, label="Gear Ratio: %.2f" % gear_ratio)

plt.xlim((0,t_max))
plt.ylim((0,30))
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
