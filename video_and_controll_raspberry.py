import cv2
import numpy as np
import socket
import struct
import threading
import tkinter as tk
current_gear=1
def receive_video(HOST, PORT):
    buffSize = 65535
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

def send_udp_message(direction, server_ip, server_port):
    gear = str(current_gear)
    message = gear + direction
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"curent gear:{gear}")
    try:
        # sock.sendto(message.encode(), (server_ip, server_port))
        print(message)
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def video_receiver_thread():
    HOST = '0.0.0.0'
    PORT = 1189
    receive_video(HOST, PORT)

def message_sender(direction):
    server_ip = "192.168.191.247"  # Replace with the receiver's IP address
    server_port = 12345  # Replace with the receiver's port
    send_udp_message(direction, server_ip, server_port)

def change_gear(gear):
    global current_gear
    if gear == 'f':
        if(current_gear < 3):
            current_gear = current_gear + 1
    if gear == 's':
        if(current_gear > 1):
            current_gear = current_gear - 1
    
root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
bottomframe = tk.Frame(root)
bottomframe.pack(side=tk.BOTTOM)
speed_up_button = tk.Button(frame, text='Speed Up', fg='green', command=lambda: change_gear('f'))
speed_up_button.pack(side=tk.LEFT)
speed_down_button = tk.Button(frame, text='Speed Down', fg='red', command=lambda: change_gear('s'))
speed_down_button.pack(side=tk.RIGHT)
upbutton = tk.Button(frame, text='↑', fg='black', command=lambda:message_sender('u'))
upbutton.pack()
leftbutton = tk.Button(bottomframe, text='←', fg='black', command=lambda:message_sender('l'))
leftbutton.pack(side=tk.LEFT)
downbutton = tk.Button(bottomframe, text='↓', fg='black', command=lambda:message_sender('d'))
downbutton.pack(side=tk.LEFT)
rightbutton = tk.Button(bottomframe, text='→', fg='black', command=lambda:message_sender('r'))
rightbutton.pack(side=tk.LEFT)
video_receiver_thread()
root.mainloop()
