import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

source_voltage=16 #V
max_pwm=255
v_per_pwm=source_voltage/max_pwm


#Datasheet https://www.mhm-modellbau.de/part-TM-RI50.php

Kv =100 #(Rpm/V)
amotor = Kv * v_per_pwm #0.2  # Coefficient for speed
Kt = 0.104 # Nm/A
resistance=0.395 #Ohm= V/A
bmotor = 0.3  # Coefficient for current in Ampere wich is proportional to torque


friction_voltage = 1.9  # Friction voltage in V from experiment
friction_pwm = friction_voltage / source_voltage * max_pwm  # Friction PWM
friction_current = friction_voltage / resistance  # Friction current in A
def calculate_voltage(speed, current, friction_pwm, amotor, bmotor):
    """
    Calculate the voltage required for a given speed and current, considering friction voltage.
    
    Arguments:
    speed (float or numpy.ndarray): The speed of the motor.
    current (float or numpy.ndarray): The current of the motor.
    friction_voltage (float): The voltage at which current and speed start due to friction and other losses.

    Returns:
    float or numpy.ndarray: The calculated voltage.
    """
    voltage = (current * bmotor + speed) / amotor
    # formula: https://h2t.iar.kit.edu/pdf/Klas2021.pdf
    # current = (voltage *amotor - n) / bmotor
    # voltage=(current*bmotor  + n)/(amotor)=
    voltage = np.where(speed >= 0, voltage + friction_pwm, voltage - friction_pwm)
    voltage = np.where(current >= 0, voltage + friction_pwm, voltage - friction_pwm)
    return voltage
   



if __name__ == "__main__":

    # Generate data
    speed_range = np.linspace(-100, 100, 100)#np.linspace(-1, 1, 2)#
    current_range = np.linspace(-50, 50, 100)
    speed_values, current_values = np.meshgrid(speed_range, current_range)

    voltage_values = calculate_voltage(speed_values, current_values, friction_pwm, amotor, bmotor)

    # Create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(voltage_values,speed_values,  current_values,  cmap='viridis')

    # Set labels and title
    ax.set_ylabel('Speed')
    ax.set_xlabel('Voltage')
    ax.set_zlabel('Current')

    ax.set_title('Voltage vs Speed and current')

    # Show plot
    plt.show()