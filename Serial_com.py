import serial
import serial.tools.list_ports
import time

def find_arduino_serial_port(baud_rate=9600, timeout=2):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "Arduino" in port.description or "Arduino" in port.manufacturer:
            return port.device
    return None


def communicate_with_arduino(port):
    ser = serial.Serial(port, 9600)
    time.sleep(2)  # wait for the serial connection to initialize
    try:
        while True:
            # Sending a string to the Arduino
            ser.write(b'Hello, Arduino!\n')
            
    except KeyboardInterrupt:
        print("Program terminated!")
    finally:
        ser.close()  # Close the serial connection

arduino_port = find_arduino_serial_port()
if arduino_port:
    print(f"Arduino found at {arduino_port}")
    communicate_with_arduino(arduino_port)
else:
    print("Arduino not found. Please check your connection.")
