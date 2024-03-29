import socket


def send_message(data):
    HOST = '127.0.0.1'
    PORT = 2424

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data.encode())
        print(f"Message sent to server: {data}")

        # receive response from the server
        response = s.recv(1024).decode()
        print(f"Response received from server: {response}")


# usage
#         client_id
#         client_type
#         message_id
#         payload

send_message("1,0,1,John Doe,Owner")  # owner registeration
send_message("2,0,2,BMW")  # owner posts a car
send_message("4,0,2,Logan")  # owner posts a car
send_message("4,1,3,BMW,John Doe")  # owner makes a query for all cars
send_message("4,1,4,BMW,John Doe")  # start rental
send_message("4,1,5,BMW,John Doe")  # end rental
send_message("4,1,4,BMW,John Doe")  # start rental again