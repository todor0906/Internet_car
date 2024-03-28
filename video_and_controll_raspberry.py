import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import socket
import struct
import threading
import queue

# Network configuration variables
video_ip = '0.0.0.0'
video_port = 1189
message_ip = "192.168.191.247"
message_port = 12345

# Initialize the frame queue and current gear
frame_queue = queue.Queue()
current_gear = 1

# Track pressed keys for diagonal movements
pressed_keys = set()

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
                continue

            timestamp, size = struct.unpack('di', packet[:12])
            data = packet[12:]

            if timestamp <= previous_timestamp or len(data) != size:
                continue

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
    global current_gear
    gear = str(current_gear)
    message = gear + direction
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending command: {message}")
    try:
        sock.sendto(message.encode(), (server_ip, server_port))
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def change_gear(gear, gear_var):
    global current_gear
    if gear == 'f' and current_gear < 3:
        current_gear += 1
    elif gear == 's' and current_gear > 1:
        current_gear -= 1
    gear_var.set('Gear: {}'.format(current_gear))

def handle_key_press(event):
    global pressed_keys
    pressed_keys.add(event.keysym.lower())
    send_diagonal_command()

def handle_key_release(event):
    global pressed_keys
    if event.keysym.lower() in pressed_keys:
        pressed_keys.remove(event.keysym.lower())

def send_diagonal_command():
    if 'w' in pressed_keys and 'd' in pressed_keys:
        send_udp_message('ur', message_ip, message_port)
    elif 'w' in pressed_keys and 'a' in pressed_keys:
        send_udp_message('ul', message_ip, message_port)
    elif 's' in pressed_keys and 'a' in pressed_keys:
        send_udp_message('dl', message_ip, message_port)
    elif 's' in pressed_keys and 'd' in pressed_keys:
        send_udp_message('dr', message_ip, message_port)
    elif 'w' in pressed_keys:
        send_udp_message('u0', message_ip, message_port)
    elif 'a' in pressed_keys:
        send_udp_message('0l', message_ip, message_port)
    elif 's' in pressed_keys:
        send_udp_message('d0', message_ip, message_port)
    elif 'd' in pressed_keys:
        send_udp_message('0r', message_ip, message_port)

def setup_gui():
    root = tk.Tk()
    image_label = ttk.Label(root)
    image_label.pack()

    gear_var = tk.StringVar()
    gear_var.set('Gear: 1')
    gear_label = ttk.Label(root, textvariable=gear_var)
    gear_label.pack()

    button_frame1 = ttk.Frame(root)
    button_frame1.pack()
    ttk.Button(button_frame1, text='↑', command=lambda: send_udp_message('u', message_ip, message_port)).pack()

    button_frame2 = ttk.Frame(root)
    button_frame2.pack()
    ttk.Button(button_frame2, text='←', command=lambda: send_udp_message('l', message_ip, message_port)).pack(side=tk.LEFT)
    ttk.Button(button_frame2, text='↓', command=lambda: send_udp_message('d', message_ip, message_port)).pack(side=tk.LEFT)
    ttk.Button(button_frame2, text='→', command=lambda: send_udp_message('r', message_ip, message_port)).pack(side=tk.LEFT)

    button_frame3 = ttk.Frame(root)
    button_frame3.pack()
    ttk.Button(button_frame3, text='Gear Up', command=lambda: change_gear('f', gear_var)).pack(side=tk.LEFT)
    ttk.Button(button_frame3, text='Gear Down', command=lambda: change_gear('s', gear_var)).pack(side=tk.RIGHT)

    # Bind the key press and key release events to the root window
    root.bind('<KeyPress>', handle_key_press)
    root.bind('<KeyRelease>', handle_key_release)
    
    # Bind the arrow keys for gear change
    root.bind('<Up>', lambda event: change_gear('f', gear_var))
    root.bind('<Down>', lambda event: change_gear('s', gear_var))

    # Start the thread to receive video frames
    threading.Thread(target=receive_video, args=(video_ip, video_port), daemon=True).start()

    # Initiate the image update loop
    update_image(image_label)

    # Start the tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    setup_gui()
