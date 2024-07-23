import serial
import keyboard
import time
global ser

def init():
    global ser
    # Set up serial communication
    print("Connecting to serial port for robot head...")
    for i in range(5):
        try:
            ser = serial.Serial('COM19', 115200)  #'COM19': bluetooth serial
            print("Serial port for robot head connected")
            return
        except:
            print("Retrying")
            print("Serial port for robot head not available")


def move(key, direction):
    global ser
    # Assuming direction is a float, convert it to bytes and concatenate with 'e'
    # command = key.encode() + str(direction).encode() #b'e1' command to move the robot eyes
    command=bytes(key + str(direction) + '\n', 'utf-8')
    ser.write(command )  
    print(f"Sent command: {command}")
    response = ser.readline().decode().strip()
    print(f"Received response: {response}")

def on_key_press(event):
    global direction  # Use global variable to keep track of direction
    if event.scan_code== 75: # 'right arrow' key code
       # direction -= .1
        #if direction < 0:
        direction = 0
        move("e",direction)
    elif event.scan_code == 77: # 'left arrow' key code
        #direction += .1
        #if direction > 1:
        direction = 1
        move("e",direction)
    elif event.scan_code == 80: # 'left arrow' key code
        #direction += .1
        #if direction > 1:
        direction = 1
        move("l",direction)
    elif event.scan_code == 72: # 'left arrow' key code
        #direction -= .1
        #if direction < 0:
        direction = 0
        move("l",direction)
    else:
        print(f"Key pressed: {event.scan_code}")  # Print the name of the key pressed

def main():
    global direction
    direction = 0.5  # Initialize direction with a neutral value
    keyboard.on_press(on_key_press)  # Register the callback for key press events
    
    while True:
        # Your loop can perform other tasks, but this example just passes time
        keyboard.read_event()  # This is to keep the loop alive without busy waiting
        time.sleep(0.01)  # Sleep for a short time to avoid high CPU usage



if __name__ == '__main__':
    init()
    main()