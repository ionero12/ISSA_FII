import socket

def start_car_client():
    HOST = '127.0.0.1'  # Server's IP address
    PORT = 2424  # Port for car client

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server.")

        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            print(f"Command received from server: {data}")
            # Perform action based on received command
            if data == "startRental":
                print("Locking the car doors...")
                s.sendall("Doors locked".encode())  # Send confirmation to server
            elif data == "endRental":
                print("Unlocking the car doors...")
                s.sendall("Doors unlocked".encode())  # Send confirmation to server
            else:
                print("Invalid command")
                s.sendall("Error: Invalid command".encode())  # Send error message to server

# Start the car client
start_car_client()
