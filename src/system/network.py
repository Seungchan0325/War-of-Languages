import platform
import select
import socket
from collections import deque
from dataclasses import dataclass

from common import SingletonInstane


@dataclass
class NetworkErros:
    def __init__(self):
        '''
        Linux
            EINPROGRESS = 115
            ECONNREFUSED = 3425
            ETIMEDOUT = 3447
            EINTR = 3407

        Windows
            WSAEWOULDBLOCK = 10035
            WSAECONNREFUSED = 10061
            WSAETIMEDOUT = 10060
            WSAEINTR = 10004

        Darwin (macOS)
            EINPROGRESS = 36
            ECONNREFUSED = 61
            ETIMEDOUT = 60
            EINTR = 4
        '''

        # Defines constants
        self.EINPROGRESS: int
        self.ECONNREFUSED: int
        self.ETIMEDOUT: int
        self.EINTR: int
        system = platform.system()
        if system == "Linux":
            self.EINPROGRESS = 115
            self.ECONNREFUSED = 3425
            self.ETIMEDOUT = 3447
            self.EINTR = 3407
        elif system == "Windows":
            self.EINPROGRESS = 10035
            self.ECONNREFUSED = 10061
            self.ETIMEDOUT = 10060
            self.EINTR = 10004
        elif system == "Darwin":
            self.EINPROGRESS = 36
            self.ECONNREFUSED = 61
            self.ETIMEDOUT = 60
            self.EINTR = 4
        else:
            assert False, "Unknown OS"


class Network(SingletonInstane):
    Addr = tuple[str, int]

    def __init__(self):

        # connection information
        self.connection: list[socket.socket] = []
        self.new_connection: list[socket.socket] = []
        self.refused: list[Network.Addr] = []
        self.sockets: dict[Network.Addr, socket.socket] = {}

        # Listening socket
        self._my_socket: socket.socket

        self._conn_que: list[Network.Addr] = []
        self._disconn: list[socket.socket] = []
        self._connecting: list[socket.socket] = []

        # variables for select
        self._potential_readers: list[socket.socket] = []
        self._potential_writers: list[socket.socket] = []
        self._potential_errs: list[socket.socket] = []

        # I/O stream
        self._input_stream: dict[socket.socket, bytearray] = {}
        self._output_stream: dict[socket.socket, deque[bytes]] = {}

        self._input_list: dict[socket.socket, list[bytearray]] = {}

        self._erros = NetworkErros()

    def _add(self, sock: socket.socket, addr: Addr):
        self.new_connection.append(sock)
        self.connection.append(sock)

        self.sockets[addr] = sock

        self._potential_readers.append(sock)
        self._potential_writers.append(sock)

        self._input_stream[sock] = bytearray()
        self._output_stream[sock] = deque()

        self._input_list[sock] = []

    def _remove(self, sock: socket.socket, addr: Addr):
        self.connection.remove(sock)

        self.sockets.pop(addr)

        self._potential_readers.remove(sock)
        self._potential_writers.remove(sock)

        self._input_stream.pop(sock)
        self._output_stream.pop(sock)

        self._input_list.pop(sock)

    # Close directly.
    def _fast_close(self, sock: socket.socket, addr: Addr):
        self._remove(sock, addr)
        sock.close()

    def init(self, addr: Addr):

        # Create listening socket
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._my_socket.setblocking(False)
        self._my_socket.bind(addr)
        self._my_socket.listen()

        self._potential_readers.append(self._my_socket)

    def update(self):
        # Reset new_connection every frame
        self.new_connection.clear()

        # disconnect
        for sock in self._disconn.copy():
            # Continue if you have data to send.
            if self._output_stream[sock]:
                continue

            addr = sock.getpeername()
            self._fast_close(sock, addr)

            self._disconn.remove(sock)

        # connect
        for addr in self._conn_que.copy():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            errno = sock.connect_ex(addr)

            self._conn_que.remove(addr)

            if errno == 0:
                # Connection successful
                self._add(sock, addr)
            elif errno == self._erros.EINPROGRESS:
                # Connecting. We need to check again
                self._connecting.append(sock)
                self._potential_writers.append(sock)
            else:
                self.refused.append(addr)

        ready_to_read: list[socket.socket]
        ready_to_write: list[socket.socket]
        in_error: list[socket.socket]

        ready_to_read, ready_to_write, in_error = select.select(
            self._potential_readers,
            self._potential_writers,
            self._potential_errs,
            0,
        )

        # write
        for sock in ready_to_write:
            # Check connecting sockets
            if sock in self._connecting:
                errno = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

                # Connection successful
                if errno == 0:
                    self._connecting.remove(sock)
                    self._potential_writers.remove(sock)

                    self._add(sock, sock.getpeername())

                # INTERRUPT ERROR. We should check it again
                elif errno == self._erros.EINTR:
                    pass

                # Connection failed
                else:
                    self.refused.append(sock.getpeername())

                    self._connecting.remove(sock)
                    self._potential_writers.remove(sock)

                    sock.close()

                continue

            # Send data
            que = self._output_stream[sock]
            while que:
                data = que.popleft() + b"\0"
                sock.send(data)

        # recv
        for sock in ready_to_read:
            # Processing connection requests
            if sock is self._my_socket:
                client, addr = sock.accept()
                self._add(client, addr)
                continue

            # Recive data
            data = sock.recv(4096)

            # Disconnected
            if not data:
                addr = sock.getpeername()
                self._fast_close(sock, addr)
                continue

            input_stream = self._input_stream[sock]
            input_stream.extend(data)

            while True:
                sep = input_stream.find(b"\0") + 1
                if sep == 0:
                    break
                self._input_list[sock].append(input_stream[:sep])
                input_stream = input_stream[sep:]

    def release(self):
        # Close all sockets
        for sock in self.connection:
            addr = sock.getpeername()
            self._fast_close(sock, addr)

        self._my_socket.close()

    def is_conn(self, addr: Addr) -> bool:
        return addr in self.sockets

    def conn(self, addr: Addr):
        self._conn_que.append(addr)

    def send(self, sock: socket.socket, data: bytes):
        output_stream = self._output_stream[sock]
        output_stream.append(data)

    def send_by_addr(self, addr: Addr, data: bytes):
        sock = self.sockets[addr]
        self.send(sock, data)

    def recv(self, sock: socket.socket) -> list[bytearray]:
        return self._input_list[sock]

    def recv_by_addr(self, addr: Addr) -> list[bytearray]:
        sock = self.sockets[addr]
        return self.recv(sock)

    def close(self, sock: socket.socket):
        self._disconn.append(sock)

    def close_by_addr(self, addr: Addr):
        sock = self.sockets[addr]
        self.close(sock)
