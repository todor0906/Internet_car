import cv2
import numpy as np
import socket
import struct
import threading
import tkinter as tk

def receive_video(HOST, PORT):
    buffSize = 6553
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    print('Waiting for video frames...')
    previous_timestamp = 0

    try:
        while True:
            packet, _ = server.recvfrom(buffSize)
            if len(packet) < 12:
                continue  # Not enough data for timestamp and size

            try:
                timestamp, size = struct.unpack('di', packet[:12])
                data = packet[12:]

                if timestamp <= previous_timestamp or len(data) != size:
                    continue  # Skip if timestamp is not newer or sizes mismatch
                previous_timestamp = timestamp

                frame = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if frame is not None:
                    cv2.imshow('Received Video', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            except cv2.error as e:
                print(f"OpenCV error: {e}")
            except struct.error as e:
                print(f"Struct unpacking error: {e}")
            root.update()
    except Exception as e:
        print(f"General error: {e}")

    finally:
        server.close()
        cv2.destroyAllWindows()

def send_udp_message(message, server_ip, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(message.encode(), (server_ip, server_port))
        print(message)
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def video_receiver_thread():
    HOST = '0.0.0.0'
    PORT = 1189
    receive_video(HOST, PORT)

def message_sender(message):
    server_ip = "192.168.191.247"  # Replace with the receiver's IP address
    server_port = 12345  # Replace with the receiver's port
    send_udp_message(message, server_ip, server_port)

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
bottomframe = tk.Frame(root)
bottomframe.pack(side=tk.BOTTOM)
upbutton = tk.Button(frame, text='↑', fg='black', command=lambda:message_sender("up"))
upbutton.pack()
leftbutton = tk.Button(bottomframe, text='←', fg='black', command=lambda:message_sender("left"))
leftbutton.pack(side=tk.LEFT)
downbutton = tk.Button(bottomframe, text='↓', fg='black', command=lambda:message_sender("down"))
downbutton.pack(side=tk.LEFT)
rightbutton = tk.Button(bottomframe, text='→', fg='black', command=lambda:message_sender("right"))
rightbutton.pack(side=tk.LEFT)
video_receiver_thread()

