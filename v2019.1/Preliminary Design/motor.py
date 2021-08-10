import numpy as np

class Motor:
    def __init__(self,
                 kv = 1000, # rpm/volt
                 resistance = 0.1, # ohms
                 no_load_current = 0.4 #amps
                 ):
        self.kv = kv
        self.resistance = resistance
        self.no_load_current = no_load_current
        self.kv_rads_per_sec_per_volt = self.kv * np.pi/30 #rads/sec/volt

    def performance(self,
                    voltage=-np.Inf,
                    current=-np.Inf,
                    rpm=-np.Inf,
                    torque=-np.Inf
                    ):
        # Input:
#       #   Exactly two of the following parameters: voltage, current, rpm, torque.
        #   Exception: You cannot supply the combination of current and torque - this makes for an ill-posed problem.
        # Output:
        #   A tuple of all four relevant parameters: (voltage, current, rpm, torque).

        # Validate inputs:
        voltage_known = voltage != -np.Inf
        current_known = current != -np.Inf
        rpm_known = rpm != -np.Inf
        torque_known = torque != -np.Inf

        assert (voltage_known + current_known + rpm_known + torque_known) == 2, "You must give exactly two input arguments."
        assert not (current_known and torque_known), "You cannot supply the combination of current and torque - this makes for an ill-posed problem."

        while not (voltage_known and current_known and rpm_known and torque_known):
            if rpm_known:
                if current_known and not voltage_known:
                    speed = rpm * np.pi / 30  # rad/sec
                    back_EMF_voltage = speed / self.kv_rads_per_sec_per_volt
                    voltage = back_EMF_voltage + current * self.resistance
                    voltage_known = True

            if torque_known:
                if not current_known:
                    current = torque * self.kv_rads_per_sec_per_volt + self.no_load_current
                    current_known = True

            if voltage_known:
                if rpm_known and not current_known:
                    speed = rpm * np.pi/30 # rad/sec
                    back_EMF_voltage = speed / self.kv_rads_per_sec_per_volt
                    current = (voltage - back_EMF_voltage) / self.resistance
                    current_known = True
                if not rpm_known and current_known:
                    back_EMF_voltage = voltage - (current * self.resistance)
                    speed = back_EMF_voltage * self.kv_rads_per_sec_per_volt
                    rpm = speed * 30 / np.pi
                    rpm_known = True


            if current_known:
                if not torque_known:
                    torque = (current - self.no_load_current) / self.kv_rads_per_sec_per_volt
                    torque_known = True

        return voltage, current, rpm, torque

# testmotor = Motor()
# print(testmotor.performance(rpm=100,current=3))
# print(testmotor.performance(rpm = 4700, torque = 0.02482817))