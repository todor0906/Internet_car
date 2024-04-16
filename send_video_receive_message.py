import cv2
import numpy as np
import socket
import struct
import time
import threading
import serial
import serial.tools.list_ports
import sys

def find_arduino_serial_port(baud_rate=9600, timeout=2):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "Arduino" in port.description or "Arduino" in port.manufacturer:
            return port.device
    return None

def find_available_camera(max_checks=10):
    for i in range(max_checks):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            cap.release()
            return i
    return None

def send_video(HOST, PORT):
    camera_index = find_available_camera()
    if camera_index is None:
        print("No camera found. Exiting...")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    capture = cv2.VideoCapture(camera_index)

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print('Sending frames...')

    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                continue

            # Encode the frame
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            data = buffer.tobytes()

            timestamp = time.time()
            timestamp_data = struct.pack('d', timestamp)

            # Send timestamp + frame size + data
            server.sendto(timestamp_data + struct.pack('i', len(data)) + data, (HOST, PORT))

            print('Frame sent')

    except Exception as e:
        print('Error:', e)

    finally:
        capture.release()
        server.close()

def receive_udp_message(listen_ip, listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))

    print(f"Listening for UDP messages on {listen_ip}:{listen_port}...")
    while True:
        data, addr = sock.recvfrom(1024) 
        message=data.decode()
        print(f"Received message: {message} from {addr}")
        ser_message = message.encode('utf-8')
        ser.write(ser_message)

arduino_port = find_arduino_serial_port()
if arduino_port:
    print(f"Arduino found at {arduino_port}")
else:
    sys.exit("Arduino not found. Please check your connection.")
ser = serial.Serial(arduino_port, 9600)
time.sleep(2)
# Video 
HOST = '10.147.18.118' 
PORT = 1189

# Message 
listen_ip = "0.0.0.0"  
listen_port = 12345  

video_thread = threading.Thread(target=send_video, args=(HOST, PORT))
video_thread.start()

receive_udp_message(listen_ip, listen_port)
