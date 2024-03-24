import socket

def receive_udp_message(listen_ip, listen_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the IP and port
    sock.bind((listen_ip, listen_port))

    print(f"Listening for UDP messages on {listen_ip}:{listen_port}...")
    while True:
        # Wait for a message
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f"Received message: {data.decode()} from {addr}")

# Example usage
listen_ip = "0.0.0.0"  # Listen on all available IPs
listen_port = 12345  # The same port as used in the sender
receive_udp_message(listen_ip, listen_port)
