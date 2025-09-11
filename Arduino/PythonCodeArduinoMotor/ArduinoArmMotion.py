import serial
import time


def send_command(command):
    ser.write(command.encode())
    while True:
        response = ser.readline().decode().strip()
        if response == "ok":
            break

deltax = 0.5	# Bewegungsschrittweite
deltay = 0.5	# Bewegungsschrittweite
# Ersetzen Sie 'COM3' durch den tatsächlichen Port des Arduino (z. B. '/dev/ttyUSB0' unter Linux).
ser = serial.Serial('COM13', 115200)
time.sleep(2)  # Kurze Pause, um sicherzustellen, dass die Verbindung aufgebaut ist.

#move a bit down

#make movement abolute
ser.write(b"G90\n")

#set as 0 point
#ser.write(b"G1 X0.2 Y-0.2 F100\n")
#pause 1 second
#time.sleep(1)
#set the 0 point
#ser.write(b"G92 X-0.1 Y0.1\n")
#ser.write(b"G10 L20 P1 X-0.2 Y0.2 Z0")
time.sleep(1)
#set the x acceleration
ser.write(b"$120=50\n")
#set the y acceleration
ser.write(b"$121=50\n")
#set the z acceleration
ser.write(b"$122=40\n")
#set the x speed
ser.write(b"$110=2000\n")
#set the y speed
ser.write(b"$111=2000\n")
#set the z speed
ser.write(b"$112=2000\n")

#move x and y
if False:
    # Send the commands x times
    for j in range(2):
        for i in range(2):
            command = f"G1 X{deltax} Y{deltay} F50\n"
            send_command(command)
            send_command("G1 X0 Y0 F50\n")
        for i in range(5):
            command = f"G1 X{deltax} Y{deltay} F500\n"
            send_command(command)
            send_command("G1 X0 Y0 F500\n")
    time.sleep(1)
    ser.close()

#move z axis up and down 1 time
if False:
    for i in range(15):
        command = f"G1 Z-0.5 F1000\n"
        send_command(command)
        command = f"G1 Z0 F300\n"
        send_command(command)
    time.sleep(1)
    ser.close()

#Torque einschalten
if True:
    ser.write(b"$1=255\n")
    ser.write(b"$C\n")
    ser.write(b"$C\n")
    time.sleep(1)
    ser.close()

#Torque ausschalten
if False:
    ser.write(b"$1=0\n")
    ser.write(b"$C\n")
    ser.write(b"$C\n")
    time.sleep(1)
    ser.close()