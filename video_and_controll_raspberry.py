import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import socket
import struct
import threading
import queue

frame_queue = queue.Queue()
current_gear = 1

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

            timestamp, size = struct.unpack('di', packet[:12])
            data = packet[12:]

            if timestamp <= previous_timestamp or len(data) != size:
                continue  # Skip if timestamp is not newer or sizes mismatch
            previous_timestamp = timestamp

            frame = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            if frame is not None:
                frame_queue.put(frame)
    except Exception as e:
        print(f"General error: {e}")
    finally:
        server.close()

def update_image(label):
    if not frame_queue.empty():
        frame = frame_queue.get()
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        imgtk = ImageTk.PhotoImage(image=pil_image)
        label.imgtk = imgtk  
        label.configure(image=imgtk)
    label.after(10, lambda: update_image(label))

def send_udp_message(direction, server_ip, server_port):
    gear = str(current_gear)
    message = gear + direction
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"current gear: {gear}, message: {message}")
    try:
        sock.sendto(message.encode(), (server_ip, server_port))
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def change_gear(gear):
    global current_gear
    if gear == 'f' and current_gear < 3:
        current_gear += 1
    elif gear == 's' and current_gear > 1:
        current_gear -= 1

def setup_gui():
    root = tk.Tk()
    image_label = ttk.Label(root)
    image_label.pack()

    frame = tk.Frame(root)
    frame.pack(side=tk.TOP)
    ttk.Button(frame, text='Speed Up', command=lambda: change_gear('f')).pack(side=tk.LEFT)
    ttk.Button(frame, text='Speed Down', command=lambda: change_gear('s')).pack(side=tk.RIGHT)
    ttk.Button(root, text='↑', command=lambda: send_udp_message('u', "192.168.191.247", 12345)).pack()
    ttk.Button(root, text='←', command=lambda: send_udp_message('l', "192.168.191.247", 12345)).pack(side=tk.LEFT)
    ttk.Button(root, text='↓', command=lambda: send_udp_message('d', "192.168.191.247", 12345)).pack(side=tk.LEFT)
    ttk.Button(root, text='→', command=lambda: send_udp_message('r', "192.168.191.247", 12345)).pack(side=tk.LEFT)

    threading.Thread(target=receive_video, args=('0.0.0.0', 1189), daemon=True).start()

    update_image(image_label)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
