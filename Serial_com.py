import serial
import serial.tools.list_ports
import time

def find_arduino_serial_port(baud_rate=9600, timeout=2):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        try:
            ser = serial.Serial(port.device, baud_rate, timeout=timeout)
            time.sleep(2)  # Allow time for serial connection to initialize
            test_byte = b'x'
            ser.write(test_byte)
            time.sleep(1)  # Wait for a response
            response = ser.read(size=1)
            ser.close()
            if response == test_byte:
                return port.device
        except (OSError, serial.SerialException):
            pass
    return None

def communicate_with_arduino(port):
    ser = serial.Serial(port, 9600)
    time.sleep(2)  # wait for the serial connection to initialize
    try:
        while True:
            # Sending a string to the Arduino
            ser.write(b'Hello, Arduino!\n')
            
            # Reading the echoed back message
            time.sleep(1)  # Give Arduino time to respond
            while ser.in_waiting:
                incomingMessage = ser.readline().decode('utf-8').rstrip()
                print(f"Received: {incomingMessage}")
            
            time.sleep(1)  # Wait a bit before sending the next message
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
