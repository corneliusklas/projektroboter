# Importing Libraries 
import serial 
import time 
arduino = serial.Serial(
    port='COM19',          # Replace with your Arduino's serial port
    baudrate=115200,      # Higher baud rate for faster communication
    timeout=0,         # Short timeout for responsiveness
    write_timeout=0,    # Short write timeout
    rtscts=True ,          # Enable RTS/CTS hardware flow control if supported
)
def write_read(x): 
	arduino.write(bytes(x +  '\n', 'utf-8')) 
	time.sleep(0.05) 
	#data = arduino.readline() 
	return "ok" #data 
while True: 
	num = input("Enter a number: ") # Taking input from user 
	value = write_read(num) 
	print(value) # printing the value 
