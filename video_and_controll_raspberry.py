import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import socket
import struct
import threading
import queue
import time

video_ip = '0.0.0.0'
video_port = 1189
message_ip = "10.147.18.247"
message_port = 12345

frame_queue = queue.Queue() #FIFO
decoded_frame_queue = queue.Queue(maxsize=2)
current_gear = 1


pressed_keys = set()

def receive_video(HOST, PORT):
    buffSize = 65535
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    print('Waiting for video frames...')

    try:
        while True:
            packet, _ = server.recvfrom(buffSize)
            if len(packet) < 12:
                continue

            timestamp, size = struct.unpack('di', packet[:12]) # 8 bytes and 4 bytes - timestamp and size of the frame
            data = packet[12:] #Rest of the packet

            if len(data) != size:
                continue

            frame_queue.put((timestamp, data))
    except Exception as e:
        print(f"General error: {e}")
    finally:
        server.close()

def decode_frames():
    last_processed_time = time.time()
    frame_skip_threshold = 10  # Number of frames in the queue before skipping
    frame_processing_limit = 1  # processing time

    while True:
        current_time = time.time()

        # Dynamic adjustment of frame skipping based on processing performance
        if frame_queue.qsize() > frame_skip_threshold or (current_time - last_processed_time < frame_processing_limit and frame_queue.qsize() > 1):
            print("Skipping frame to catch up...")
            frame_queue.get()  # Skip this frame
            continue

        if not frame_queue.empty():
            timestamp, data = frame_queue.get()

            frame = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            if frame is not None:
                if decoded_frame_queue.full():
                    decoded_frame_queue.get_nowait()  # Remove the oldest frame
                decoded_frame_queue.put(frame)

            last_processed_time = time.time()

        # Adjust frame_skip_threshold based on processing performance
        if frame_queue.qsize() < 5:
            frame_skip_threshold = max(10, frame_skip_threshold - 1)
        else:
            frame_skip_threshold = min(20, frame_skip_threshold + 1)


def update_image(label):
    try:
        if not decoded_frame_queue.empty():
            frame = decoded_frame_queue.get()
            cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv_image)
            imgtk = ImageTk.PhotoImage(image=pil_image)
            label.imgtk = imgtk  # Prevent garbage collection
            label.configure(image=imgtk)
    finally:
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

    root.bind('<KeyPress>', handle_key_press)
    root.bind('<KeyRelease>', handle_key_release)
    
    root.bind('<Up>', lambda event: change_gear('f', gear_var))
    root.bind('<Down>', lambda event: change_gear('s', gear_var))

    threading.Thread(target=receive_video, args=(video_ip, video_port), daemon=True).start()
    threading.Thread(target=decode_frames, daemon=True).start()
    update_image(image_label)
    
    root.mainloop()
def key_press(button, pressed_keys, key):
    pressed_keys.add(key)
    update_direction(pressed_keys)

def key_release(pressed_keys, key):
    pressed_keys.discard(key)
    update_direction(pressed_keys)

def update_direction(pressed_keys):
    direction = ''.join(sorted(pressed_keys))
    send_udp_message(direction, message_ip, message_port)

if __name__ == "__main__":
    setup_gui()
