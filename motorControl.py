import serial
import keyboard

# Adjust these variables according to your setup
serial_port = 'COM13' #'/dev/ttyACM0' # Serial port Arduino is connected to (e.g., COM3 on Windows)
baud_rate = 500000 # Match baud rate to Arduino sketch
pwm_value = 128 # Initial PWM value

# Open serial connection to Arduino
arduino = serial.Serial(serial_port, baud_rate, timeout=1)

def adjust_pwm(change):
    global pwm_value
    pwm_value = max(0, min(255, pwm_value + change)) # Ensure PWM is within 0-255
    arduino.write(f"{pwm_value}\n".encode()) # write as string
    print(f"PWM: {pwm_value}")

try:
    print("Use 'up' to increase and 'down' to decrease PWM. Press 'ESC' to exit.")
    while True:
        if keyboard.is_pressed('up'): # Increase PWM
            adjust_pwm(10) # Adjust the increment value as needed
            while keyboard.is_pressed('up'): pass # Wait for key release

        if keyboard.is_pressed('down'): # Decrease PWM
            adjust_pwm(-10) # Adjust the decrement value as needed
            while keyboard.is_pressed('down'): pass # Wait for key release

        if keyboard.is_pressed('esc'): # Exit program
            print("Exiting...")
            break

finally:
    arduino.close() # Ensure serial connection is closed on exit
