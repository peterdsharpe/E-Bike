import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.library.propulsion_electric as prop_elec
from scipy import integrate, optimize

atmo = asb.Atmosphere(altitude=0)


class Motor:
    def __init__(self,
                 kv,
                 resistance,
                 no_load_current,
                 rated_current,
                 ):
        self.kv = kv
        self.resistance = resistance
        self.no_load_current = no_load_current
        self.rated_current = rated_current

    def performance(self,
                    voltage=None,
                    current=None,
                    rpm=None,
                    torque=None,
                    ):
        return prop_elec.motor_electric_performance(
            voltage=voltage,
            current=current,
            rpm=rpm,
            torque=torque,
            kv=self.kv,
            resistance=self.resistance,
            no_load_current=self.no_load_current,
        )

    def estimate_max_heat_dissipation(self):
        ### Find the max-power condition
        def power(rpm):
            perf = self.performance(
                rpm=rpm,
                current=self.rated_current,
            )
            return perf['rpm'] * np.pi / 30 * perf['torque']

        res = optimize.minimize(
            fun = lambda x: -power(x),
            x0=0
        )

        return res

class Bike:
    def __init__(self,
                 motor=Motor(
                     kv=149,
                     resistance=0.043,
                     no_load_current=1.3,
                     rated_current=80,
                 ),
                 gear_ratio=0.083 / 0.700,
                 wheel_diameter=0.700,
                 max_voltage=3.7 * 6,
                 max_current=80,
                 mass=80,
                 ):
        self.motor = motor
        self.gear_ratio = gear_ratio
        self.wheel_diameter = wheel_diameter
        self.max_voltage = max_voltage
        self.max_current = max_current
        self.mass = mass

    def performance(self,
                    speed,
                    throttle_state=1,
                    grade=0,
                    headwind=0,
                    ):
        ##### Figure out electric thrust force

        wheel_radius = self.wheel_diameter / 2
        wheel_rads_per_sec = speed / wheel_radius
        wheel_rpm = wheel_rads_per_sec * 30 / np.pi
        motor_rpm = wheel_rpm / self.gear_ratio

        ### Limit performance by either max voltage or max current
        perf_via_max_voltage = self.motor.performance(
            voltage=self.max_voltage,
            rpm=motor_rpm,
        )
        perf_via_throttle = self.motor.performance(
            current=self.max_current * throttle_state,
            rpm=motor_rpm,
        )

        if perf_via_max_voltage['torque'] > perf_via_throttle['torque']:
            perf = perf_via_throttle
        else:
            perf = perf_via_max_voltage

        motor_torque = perf['torque']
        wheel_torque = motor_torque / self.gear_ratio
        wheel_force = wheel_torque / wheel_radius

        thrust = wheel_force
        efficiency = perf["efficiency"]

        ##### Gravity

        gravity_drag = 9.81 * np.sin(np.arctan(grade)) * self.mass

        ##### Rolling Resistance

        # Crr = 0.0020  # Concrete
        Crr = 0.0050  # Asphalt
        # Crr = 0.0060  # Gravel
        # Crr = 0.0070  # Grass
        # Crr = 0.0200  # Off-road
        # Crr = 0.0300  # Sand
        rolling_drag = 9.81 * np.cos(np.arctan(grade)) * self.mass * Crr

        ##### Aerodynamics
        # CDA = 0.408  # Tops
        CDA = 0.324  # Hoods
        # CDA = 0.307  # Drops
        # CDA = 0.2914  # Aerobars

        eff_speed = speed + headwind
        air_drag = 0.5 * atmo.density() * eff_speed * np.abs(eff_speed) * CDA

        ##### Summation
        net_force = thrust - gravity_drag - rolling_drag - air_drag
        net_accel = net_force / self.mass

        return {
            "net acceleration": net_accel,
            "efficiency": efficiency
        }

    def equations_of_motion(self, t, y):
        return np.array([
            y[1],
            self.performance(speed=y[1])["net acceleration"]
        ])

    def simulate(self,
                 t_eval,
                 t_span=(0, 60),
                 initial_position=0,
                 initial_velocity=0,
                 ):
        res = integrate.solve_ivp(
            fun=self.equations_of_motion,
            t_span=t_span,
            y0=np.array([initial_position, initial_velocity]),
            t_eval=t_eval,
        )
        return res.y


if __name__ == '__main__':

    bike = Bike()

    from aerosandbox.tools.pretty_plots import plt, show_plot, set_ticks

    fig, ax = plt.subplots()
    t = np.linspace(0, 60, 500)
    pos, vel = bike.simulate(t)
    plt.plot(t, vel * 2.24)
    set_ticks(2, 1, 4, 2)
    plt.xlim(0, 20)
    plt.ylim(0, 36)
    show_plot(
        "Electric Bike",
        xlabel="Time [s]",
        ylabel="Speed [mph]"
    )
