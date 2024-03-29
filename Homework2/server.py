import socket

registered_cars = {}

def handle_message(data, conn):
    client_id, client_type, message_id, *payload = data.split(',')

    if client_type == "0":  # owner
        if message_id == "1":
            conn.sendall("Owner registered successfully.".encode())
        elif message_id == "2":  # post car
            post_car(payload, conn)
        else:
            conn.sendall("Invalid message received from Owner".encode())
    elif client_type == "1":  # renter
        if message_id == "0":
            conn.sendall("Renter registered successfully.".encode())
        elif message_id == "3":  # request car
            query_available_cars(conn)
        elif message_id == "4":  # start rental
            start_rental(payload, conn)
        elif message_id == "5":  # end rental
            end_rental(payload, conn)
        else:
            conn.sendall("Invalid message received from Renter".encode())
    else:
        conn.sendall("Invalid client type".encode())

def post_car(payload, conn):
    car_id = payload[0]
    if car_id not in registered_cars:
        registered_cars[car_id] = {
            'available': True
        }
        conn.sendall("Car registered successfully.".encode())
    else:
        conn.sendall("Car is already registered.".encode())

def query_available_cars(conn):
    available_cars = [car_id for car_id, details in registered_cars.items() if details['available']]
    conn.sendall(f"Available cars: {', '.join(available_cars)}".encode())

def start_rental(payload, conn):
    car_id = payload[0]
    if car_id in registered_cars and registered_cars[car_id]['available']:
        registered_cars[car_id]['available'] = False
        conn.sendall("Car rented successfully.".encode())
        notify_car(car_id, "startRental")  # Notify car to unlock doors
    else:
        conn.sendall("Car is not available".encode())

def end_rental(payload, conn):
    car_id = payload[0]
    if car_id in registered_cars and not registered_cars[car_id]['available']:
        registered_cars[car_id]['available'] = True
        conn.sendall("Rental ended successfully.".encode())
        notify_car(car_id, "endRental")  # Notify car to lock doors
    else:
        conn.sendall("Car is not currently rented.".encode())

def notify_car(car_id, message):
    try:
        # Create a new connection to the car client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as car_connection:
            car_connection.connect((HOST, PORT))  # Use the correct host and port for the car client
            car_connection.sendall(message.encode())
    except KeyError:
        print("Car is not registered.")
    except Exception as e:
        print(f"An error occurred: {e}")


HOST = '127.0.0.1'
PORT = 2424

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    print(f"Received message: {data}")
                    handle_message(data, conn)
                except socket.timeout:
                    print("No data received from client for 5 seconds, closing connection.")
                    break
                except Exception as e:
                    print(f"An error occurred: {e}")
            print("Connection closed.")

