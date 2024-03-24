import cv2
import numpy as np
import socket
import struct
import time

def find_available_camera(max_checks=10):
    for i in range(max_checks):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            cap.release()
            return i
    return None  # No camera found

HOST = '192.168.191.118'  # The receiver's IP address
PORT = 1189

camera_index = find_available_camera()
if camera_index is None:
    print("No camera found. Exiting...")
    exit()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
capture = cv2.VideoCapture(camera_index)

# Adjust the camera resolution if necessary
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

        # Timestamp the frame
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
