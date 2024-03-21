import cv2
import numpy as np
import socket
import struct
import time
import threading

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

def receive_udp_message(listen_ip, listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))

    print(f"Listening for UDP messages on {listen_ip}:{listen_port}...")
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f"Received message: {data.decode()} from {addr}")

# Video sending configuration
HOST = '192.168.191.118'  # The receiver's IP address
PORT = 1189

# Message receiving configuration
listen_ip = "0.0.0.0"  # Listen on all available IPs
listen_port = 12345  # The port to listen for incoming messages

# Start the video sending in a separate thread
video_thread = threading.Thread(target=send_video, args=(HOST, PORT))
video_thread.start()

# Start the message receiving in the main thread
receive_udp_message(listen_ip, listen_port)
