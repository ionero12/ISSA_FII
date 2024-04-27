import datetime
import pickle
import socket
from typing import *

import select


class ObjectSocketParams:
    """
    A class containing parameters used by ObjectSenderSocket and ObjectReceiverSocket.

    Attributes:
        OBJECT_HEADER_SIZE_BYTES (int): The size, in bytes, of the header used for sending and receiving objects.
        DEFAULT_TIMEOUT_S (float): The default timeout value, in seconds, used for socket operations.
        CHUNK_SIZE_BYTES (int): The size, in bytes, of the chunks used for sending and receiving data over the socket connection.
    """

    OBJECT_HEADER_SIZE_BYTES = 4

    DEFAULT_TIMEOUT_S = 1

    CHUNK_SIZE_BYTES = 1024


class ObjectSenderSocket:
    """
    A class for sending objects over a socket connection.

    Attributes:
        ip (str): The IP address to bind the socket to.
        port (int): The port to bind the socket to.
        sock (socket.socket): The socket object.
        conn (socket.socket): The connection socket object.
        print_when_awaiting_receiver (bool): Whether to print messages when awaiting receiver connection.
        print_when_sending_object (bool): Whether to print messages when sending an object.

    Methods:
        __init__: Initializes the ObjectSenderSocket.
        await_receiver_connection: Waits for the receiver to connect.
        close: Closes the connection.
        is_connected: Checks if the socket is connected.
        send_object: Sends an object over the socket connection.
    """

    ip: str

    port: int

    sock: socket.socket

    conn: socket.socket

    print_when_awaiting_receiver: bool

    print_when_sending_object: bool

    def __init__(self, ip: str, port: int, print_when_awaiting_receiver: bool = False,
                 print_when_sending_object: bool = False):
        """
        Initializes the ObjectSenderSocket.

        Args:
            ip (str): The IP address to bind the socket to.
            port (int): The port to bind the socket to.
            print_when_awaiting_receiver (bool, optional): Whether to print messages when awaiting receiver connection.
            print_when_sending_object (bool, optional): Whether to print messages when sending an object.
        """

        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.conn = Noneca

        self.print_when_awaiting_receiver = print_when_awaiting_receiver
        self.print_when_sending_object = print_when_sending_object

        self.await_receiver_conection()

    def await_receiver_conection(self):
        """
        Waits for the receiver to connect.
        """

        if self.print_when_awaiting_receiver:
            print(
                f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] awaiting receiver connection...')

        self.sock.listen(1)
        self.conn, _ = self.sock.accept()

        if self.print_when_awaiting_receiver:
            print(f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] receiver connected')

    def close(self):
        """
        Closes the connection.
        """

        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """
        Checks if the socket is connected.

        Returns:
            bool: True if the socket is connected, False otherwise.
        """

        return self.conn is not None

    def send_object(self, obj: Any):
        """
        Sends an object over the socket connection.

        Args:
            obj (Any): The object to send.
        """

        data = pickle.dumps(obj)
        data_size = len(data)
        data_size_encoded = data_size.to_bytes(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES, 'little')
        self.conn.sendall(data_size_encoded)
        self.conn.sendall(data)
        if self.print_when_sending_object:
            print(
                f'[{datetime.datetime.now()}][ObjectSenderSocket/{self.ip}:{self.port}] Sent object of size {data_size} bytes.')


class ObjectReceiverSocket:
    """
    A class for receiving objects over a socket connection.

    Attributes:
        ip (str): The IP address to connect to.
        port (int): The port to connect to.
        conn (socket.socket): The connection socket object.
        print_when_connecting_to_sender (bool): Whether to print messages when connecting to the sender.
        print_when_receiving_object (bool): Whether to print messages when receiving an object.

    Methods:
        __init__: Initializes the ObjectReceiverSocket.
        connect_to_sender: Connects to the sender.
        close: Closes the connection.
        is_connected: Checks if the socket is connected.
        recv_object: Receives an object over the socket connection.
    """

    ip: str

    port: int

    conn: socket.socket

    print_when_connecting_to_sender: bool

    print_when_receiving_object: bool

    def __init__(self, ip: str, port: int, print_when_connecting_to_sender: bool = False,
                 print_when_receiving_object: bool = False):
        """
        Initializes the ObjectReceiverSocket.

        Args:
            ip (str): The IP address to connect to.
            port (int): The port to connect to.
            print_when_connecting_to_sender (bool, optional): Whether to print messages when connecting to the sender.
            print_when_receiving_object (bool, optional): Whether to print messages when receiving an object.
        """

        self.ip = ip
        self.port = port
        self.print_when_connecting_to_sender = print_when_connecting_to_sender
        self.print_when_receiving_object = print_when_receiving_object

        self.connect_to_sender()

    def connect_to_sender(self):
        """
        Connects to the sender.
        """

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connecting to sender...')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip, self.port))

        if self.print_when_connecting_to_sender:
            print(f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] connected to sender')

    def close(self):
        """
        Closes the connection.
        """

        self.conn.close()
        self.conn = None

    def is_connected(self) -> bool:
        """
        Checks if the socket is connected.

        Returns:
            bool: True if the socket is connected, False otherwise.
        """

        return self.conn is not None

    def recv_object(self) -> Any:
        """
        Receives an object over the socket connection.

        Returns:
            Any: The received object.
        """

        obj_size_bytes = self._recv_object_size()
        data = self._recv_all(obj_size_bytes)
        obj = pickle.loads(data)
        if self.print_when_receiving_object:
            print(
                f'[{datetime.datetime.now()}][ObjectReceiverSocket/{self.ip}:{self.port}] Received object of size {obj_size_bytes} bytes.')
        return obj

    def _recv_with_timeout(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> Optional[
        bytes]:
        """
        Receives data with a specified timeout.

        Args:
            n_bytes (int): The number of bytes to receive.
            timeout_s (float, optional): The timeout value in seconds. Defaults to DEFAULT_TIMEOUT_S.

        Returns:
            Optional[bytes]: The received data, or None if the timeout elapsed.
        """

        rlist, _1, _2 = select.select([self.conn], [], [], timeout_s)
        if rlist:
            data = self.conn.recv(n_bytes)
            return data
        else:
            return None  # Only returned on timeout

    def _recv_all(self, n_bytes: int, timeout_s: float = ObjectSocketParams.DEFAULT_TIMEOUT_S) -> bytes:
        """
        Receives all data with a specified timeout.

        Args:
            n_bytes (int): The total number of bytes to receive.
            timeout_s (float, optional): The timeout value in seconds. Defaults to DEFAULT_TIMEOUT_S.

        Raises:
            socket.error: If the timeout elapses without receiving all data.

        Returns:
            bytes: The received data.
        """

        data = []
        left_to_recv = n_bytes
        while left_to_recv > 0:
            desired_chunk_size = min(ObjectSocketParams.CHUNK_SIZE_BYTES, left_to_recv)
            chunk = self._recv_with_timeout(desired_chunk_size, timeout_s)
            if chunk is not None:
                data += [chunk]
                left_to_recv -= len(chunk)
            else:  # no more data incoming, timeout
                bytes_received = sum(map(len, data))
                raise socket.error(f'Timeout elapsed without any new data being received. '
                                   f'{bytes_received} / {n_bytes} bytes received.')
        data = b''.join(data)
        return data

    def _recv_object_size(self) -> int:
        """
        Receives the size of the object.

        Returns:
            int: The size of the object in bytes.
        """

        data = self._recv_all(ObjectSocketParams.OBJECT_HEADER_SIZE_BYTES)
        obj_size_bytes = int.from_bytes(data, 'little')
        return obj_size_bytes
