<<<<<<< HEAD
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import numpy as np
import keyboard

pwm_value = 0  # Initial PWM value

# Setup the serial connection
ser = serial.Serial('COM14', 9600, timeout=1)  # Adjust COM port and baud rate as needed

# Initialize plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

# Initialize lines for each plot
line_mA, = ax1.plot([], [], label='mA')
line_mS, = ax2.plot([], [], label='mS')
line_mC, = ax3.plot([], [], label='mC')

# Setting titles for each subplot
ax1.set_title('mA Measurement')
ax2.set_title('mS Measurement')
ax3.set_title('mC Measurement')

# Initialize a window of data
window_size = 100
data_mA = np.empty(0)
data_mS = np.empty(0)
data_mC = np.empty(0)

min_mA = 0
max_mA = 0 
min_mS = 0
max_mS = 0
min_mC = 0
max_mC = 0

def init():
    ax1.set_xlim(0, window_size)
    ax2.set_xlim(0, window_size)
    ax3.set_xlim(0, window_size)
    #ax1.set_ylim(-15, 15)  # Adjust based on expected mA values
    #ax2.set_ylim(-100, 100)  # Adjust based on expected mS values
    #ax3.set_ylim(-1000, 1000)  # Adjust based on expected mC values
    return line_mA, line_mS, line_mC

def adjust_pwm(change):
    global pwm_value
    pwm_value = max(-255, min(255, pwm_value + change)) # Ensure PWM is within -255-255
    ser.write(f"{pwm_value}\n".encode()) # write as string
    print(f"PWM: {pwm_value}")

def parse_serial_data(line):
    try:
        parts = line.split(',')
        mA = float(parts[0].split(':')[1])
        mS = float(parts[1].split(':')[1])
        mC = float(parts[2].split(':')[1])
        return mA, mS, mC
    except:
        return None, None, None

def update_plot(frame):
    try:
        line = ser.readline().decode('utf-8').strip()
    except:
        line=""
    #print(line)
    mA, mS, mC = parse_serial_data(line)
    if mA is not None:
        global data_mA, data_mS, data_mC
        data_mA = np.append(data_mA, mA)[-window_size:]
        data_mS = np.append(data_mS, mS)[-window_size:]
        data_mC = np.append(data_mC, mC)[-window_size:]

        line_mA.set_data(np.arange(len(data_mA)), data_mA)
        line_mS.set_data(np.arange(len(data_mS)), data_mS)
        line_mC.set_data(np.arange(len(data_mC)), data_mC)



        if frame%50==0:
            #calculate the total max and min
            global min_mA, max_mA, min_mS, max_mS, min_mC, max_mC
            min_mA = min(min(data_mA), min_mA)
            max_mA = max(max(data_mA), max_mA)
            min_mS = min(min(data_mS), min_mS)
            max_mS = max(max(data_mS), max_mS)
            min_mC = min(min(data_mC), min_mC)
            max_mC = max(max(data_mC), max_mC)



            # Adjust y-axis limits based on current data
            ax1.set_ylim(min_mA - .1, max_mA + .1)
            ax2.set_ylim(min_mS - .1, max_mS + .1)
            ax3.set_ylim(min_mC - .1, max_mC + .1)


            # Re-draw the background of the axis to apply the limit changes
            #ax1.relim()
            #ax1.autoscale_view(True, True, True)
            #ax2.relim()
            #ax2.autoscale_view(True, True, True)
            #ax3.relim()
            #ax3.autoscale_view(True, True, True)
            fig.canvas.draw()

        if keyboard.is_pressed('up'): # Increase PWM
            adjust_pwm(10) # Adjust the increment value as needed
            while keyboard.is_pressed('up'): pass # Wait for key release

        if keyboard.is_pressed('down'): # Decrease PWM
            adjust_pwm(-10) # Adjust the decrement value as needed
            while keyboard.is_pressed('down'): pass # Wait for key release


    return line_mA, line_mS, line_mC






print("Use 'up' to increase and 'down' to decrease PWM. Press 'ESC' to exit.")
ani = FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=1)  #blit=False: Update complete canvas

plt.tight_layout()
=======
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import numpy as np
import keyboard

pwm_value = 0  # Initial PWM value

# Setup the serial connection
ser = serial.Serial('COM14', 9600, timeout=1)  # Adjust COM port and baud rate as needed

# Initialize plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

# Initialize lines for each plot
line_mA, = ax1.plot([], [], label='mA')
line_mS, = ax2.plot([], [], label='mS')
line_mC, = ax3.plot([], [], label='mC')

# Setting titles for each subplot
ax1.set_title('mA Measurement')
ax2.set_title('mS Measurement')
ax3.set_title('mC Measurement')

# Initialize a window of data
window_size = 100
data_mA = np.empty(0)
data_mS = np.empty(0)
data_mC = np.empty(0)

min_mA = 0
max_mA = 0 
min_mS = 0
max_mS = 0
min_mC = 0
max_mC = 0

def init():
    ax1.set_xlim(0, window_size)
    ax2.set_xlim(0, window_size)
    ax3.set_xlim(0, window_size)
    #ax1.set_ylim(-15, 15)  # Adjust based on expected mA values
    #ax2.set_ylim(-100, 100)  # Adjust based on expected mS values
    #ax3.set_ylim(-1000, 1000)  # Adjust based on expected mC values
    return line_mA, line_mS, line_mC

def adjust_pwm(change):
    global pwm_value
    pwm_value = max(-255, min(255, pwm_value + change)) # Ensure PWM is within -255-255
    ser.write(f"{pwm_value}\n".encode()) # write as string
    print(f"PWM: {pwm_value}")

def parse_serial_data(line):
    try:
        parts = line.split(',')
        mA = float(parts[0].split(':')[1])
        mS = float(parts[1].split(':')[1])
        mC = float(parts[2].split(':')[1])
        return mA, mS, mC
    except:
        return None, None, None

def update_plot(frame):
    try:
        line = ser.readline().decode('utf-8').strip()
    except:
        line=""
    #print(line)
    mA, mS, mC = parse_serial_data(line)
    if mA is not None:
        global data_mA, data_mS, data_mC
        data_mA = np.append(data_mA, mA)[-window_size:]
        data_mS = np.append(data_mS, mS)[-window_size:]
        data_mC = np.append(data_mC, mC)[-window_size:]

        line_mA.set_data(np.arange(len(data_mA)), data_mA)
        line_mS.set_data(np.arange(len(data_mS)), data_mS)
        line_mC.set_data(np.arange(len(data_mC)), data_mC)



        if frame%50==0:
            #calculate the total max and min
            global min_mA, max_mA, min_mS, max_mS, min_mC, max_mC
            min_mA = min(min(data_mA), min_mA)
            max_mA = max(max(data_mA), max_mA)
            min_mS = min(min(data_mS), min_mS)
            max_mS = max(max(data_mS), max_mS)
            min_mC = min(min(data_mC), min_mC)
            max_mC = max(max(data_mC), max_mC)



            # Adjust y-axis limits based on current data
            ax1.set_ylim(min_mA - .1, max_mA + .1)
            ax2.set_ylim(min_mS - .1, max_mS + .1)
            ax3.set_ylim(min_mC - .1, max_mC + .1)


            # Re-draw the background of the axis to apply the limit changes
            #ax1.relim()
            #ax1.autoscale_view(True, True, True)
            #ax2.relim()
            #ax2.autoscale_view(True, True, True)
            #ax3.relim()
            #ax3.autoscale_view(True, True, True)
            fig.canvas.draw()

        if keyboard.is_pressed('up'): # Increase PWM
            adjust_pwm(10) # Adjust the increment value as needed
            while keyboard.is_pressed('up'): pass # Wait for key release

        if keyboard.is_pressed('down'): # Decrease PWM
            adjust_pwm(-10) # Adjust the decrement value as needed
            while keyboard.is_pressed('down'): pass # Wait for key release


    return line_mA, line_mS, line_mC






print("Use 'up' to increase and 'down' to decrease PWM. Press 'ESC' to exit.")
ani = FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=1)  #blit=False: Update complete canvas

plt.tight_layout()
>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
plt.show()