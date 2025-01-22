import serial
import keyboard
import time
global ser
global eyepos
eyepos = 0.5
global rotpos
rotpos = 0.5

PRINT=False

def init():
    global ser
    # Set up serial communication
    print("Connecting to serial port for robot head...")
    for i in range(5):
        try:
            ser = serial.Serial('COM26', 115200)  #'COM19': bluetooth serial
            print("Serial port for robot head connected")
            return
        except:
            print("Retrying")
            print("Serial port for robot head not available")


def move(key, postion):
    global ser
    # Assuming postion is a float, convert it to bytes and concatenate with 'e'
    # command = key.encode() + str(postion).encode() #b'e1' command to move the robot eyes
    command=bytes(key + str(postion) + '\n', 'utf-8')
    ser.write(command )  
    response = ser.readline().decode().strip()
    if PRINT:
        print(f"Sent command: {command}")
        #read all lines
        #response = ser.readlines().decode().strip()
        print(f"Received response: {response}")

#keys:
#  case 'l':  l_lid , r_lid 
#  case 'e': r_eye , l_eye 
#  case 'b': r_brow , l_brow =
#  case 'u': upper_lip = 
#    case 'w': lower_lip 
# case 'r': rotate head
#led case 'g': green/red y: yellow
def on_key_press(event):
    global eyepos  # Use global variable to keep track of postion
    global rotpos
    #eyes
    if event.scan_code== 75: # 'right arrow' key code
        eyepos += 0.25
        if eyepos > 1:
            eyepos = 1
        move("e",eyepos)
    elif event.scan_code == 77: # 'left arrow' key code
        eyepos -= .25
        if eyepos < 0:
            eyepos = 0
        move("e",eyepos)
    #eyelids
    elif event.scan_code == 80: # 'down arrow' key code
        postion = 1
        move("l",postion)
    elif event.scan_code == 72: # 'up arrow' key code
        postion = 0
        move("l",postion)
    #upper mouth open
    elif event.scan_code == 17: # 'w' key code
        postion = 1
        move("u",postion)
    #upper mouth close
    elif event.scan_code == 16: # 'q' key code
        postion = 0
        move("u",postion)
    #lower mouth open
    elif event.scan_code == 18: # 'e' key code
        postion = 1
        move("w",postion)
    #lower mouth close
    elif event.scan_code == 19: # 'r' key code
        postion = 0
        move("w",postion)
    #eybrows
    elif event.scan_code == 20: # 't' key code
        postion = 1
        move("b",postion)
    elif event.scan_code == 21: # 'y' key code	
        postion =0
        move("b",postion)
    #head rotation
    elif event.scan_code == 30: # 'a' key code
        rotpos += 0.1
        if rotpos > 1:
            rotpos = 1
        move("r",rotpos)
    elif event.scan_code == 31: # 's' key code
        rotpos -= 0.1
        if rotpos < 0:
            rotpos = 0
        move("r",rotpos)
    #leds
    elif event.scan_code == 32: # 's' key code
        move("g",1) # green on/red off
    elif event.scan_code == 33: # 'd' key code
        move("g",0) # green off/red on
    elif event.scan_code == 34: # 'f' key code
        move("y",1) # yellow on
    elif event.scan_code == 35: # 'g' key code
        move("y",0) # yellow off
    else:
        print(f"Key pressed: {event.scan_code}")  # Print the name of the key pressed

def main():
    global postion
    postion = 0.5  # Initialize postion with a neutral value
    keyboard.on_press(on_key_press)  # Register the callback for key press events
    
    while True:
        # Your loop can perform other tasks, but this example just passes time
        keyboard.read_event()  # This is to keep the loop alive without busy waiting
        time.sleep(0.01)  # Sleep for a short time to avoid high CPU usage



if __name__ == '__main__':
    init()
    main()