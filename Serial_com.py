import serial
import time

# Replace '/dev/ttyUSB0' with the port where your Arduino is connected
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)  # wait for the serial connection to initialize

try:
    while True:
        # Sending a string to the Arduino
        ser.write(b'Hello, Arduino!\n')
        
        # Reading the echoed back message
        if ser.in_waiting:
            incomingMessage = ser.readline().decode('utf-8').rstrip()
            print(f"Received: {incomingMessage}")
        
        # Wait a bit before sending the next message
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated!")

ser.close()  # Close the serial connection
