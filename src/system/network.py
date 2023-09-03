import socket
import select
import platform
from collections import deque

from common import SingletonInstane


class Network(SingletonInstane):
    Addr = tuple[str, int]

    def __init__(self):
        self.new_connection: list[socket.socket] = []
        self.refused: list[Network.Addr] = []
        self._connecting: list[socket.socket] = []
        self._disconn: list[socket.socket] = []

        self.connection: list[socket.socket] = []
        self.sockets: dict[Network.Addr, socket.socket] = {}

        self._my_socket: socket.socket

        self._potential_readers: list[socket.socket] = []
        self._potential_writers: list[socket.socket] = []
        self._potential_errs: list[socket.socket] = []

        self._input_stream: dict[socket.socket, deque[bytes]] = {}
        self._output_stream: dict[socket.socket, deque[bytes]] = {}

        self._conn_que: list[Network.Addr] = []

        # Defines constants
        self.EINPROGRESS: int
        self.ECONNREFUSED: int
        self.ETIMEDOUT: int
        self.EINTR: int
        system = platform.system()
        if system == "Linux":
            # EINPROGRESS = 115
            self.EINPROGRESS = 115
            # ECONNREFUSED = 3425
            self.ECONNREFUSED = 3425
            # ETIMEDOUT = 3447
            self.ETIMEDOUT = 3447
            # EINTR = 3407
            self.EINTR = 3407
        elif system == "Windows":
            # WSAEWOULDBLOCK = 10035
            self.EINPROGRESS = 10035
            # WSAECONNREFUSED = 10061
            self.ECONNREFUSED = 10061
            # WSAETIMEDOUT = 10060
            self.ETIMEDOUT = 10060
            # WSAEINTR = 10004
            self.EINTR = 10004
        elif system == "Darwin":
            # EINPROGRESS = 36
            self.EINPROGRESS = 36
            # ECONNREFUSED = 61
            self.ECONNREFUSED = 61
            # ETIMEDOUT = 60
            self.ETIMEDOUT = 60
            # EINTR = 4
            self.EINTR = 4
        else:
            assert False, "Unknown OS"

    def _add(self, sock: socket.socket, addr: Addr):
        self.new_connection.append(sock)
        self.connection.append(sock)
        self.sockets[addr] = sock
        self._potential_readers.append(sock)
        self._potential_writers.append(sock)
        self._input_stream[sock] = deque()
        self._output_stream[sock] = deque()

    def _remove(self, sock: socket.socket, addr: Addr):
        self.connection.remove(sock)
        self.sockets.pop(addr)
        self._potential_readers.remove(sock)
        self._potential_writers.remove(sock)
        self._input_stream.pop(sock)
        self._output_stream.pop(sock)

    def _fast_close(self, sock: socket.socket, addr: Addr):
        self._remove(sock, addr)
        sock.close()

    def init(self, addr: Addr):

        # init my socket
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._my_socket.setblocking(False)
        self._my_socket.bind(addr)
        self._my_socket.listen()
        self._potential_readers.append(self._my_socket)

    def update(self):
        self.new_connection.clear()

        for sock in self._disconn:
            if self._output_stream[sock]:
                continue
            self._disconn.remove(sock)
            self._remove(sock, sock.getpeername())
            sock.close()

        for addr in self._conn_que:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            errno = sock.connect_ex(addr)

            if errno == 0:
                self._add(sock, addr)
                self._conn_que.remove(addr)
            elif errno == self.EINPROGRESS:
                self._conn_que.remove(addr)
                self._connecting.append(sock)
                self._potential_writers.append(sock)
            else:
                self._conn_que.remove(addr)
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

        for sock in ready_to_write:
            if sock in self._connecting:
                errno = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if errno == 0:
                    self._connecting.remove(sock)
                    self._potential_writers.remove(sock)
                    self._add(sock, sock.getpeername())
                elif errno == self.EINTR:
                    pass
                else:
                    self._connecting.remove(sock)
                    self.refused.append(sock.getpeername)
                    self._potential_writers.remove(sock)
                    sock.close()
                continue

            que = self._output_stream[sock]
            while que:
                data = que.popleft()
                print("write", data)
                sock.send(data)

        for sock in ready_to_read:
            if sock is self._my_socket:
                client, addr = sock.accept()
                print("accept")
                self._add(client, addr)
            else:
                data = sock.recv(1024)

                if data:
                    self._input_stream[sock].append(data)
                    print("recv, ", data)
                else:
                    print("discon")
                    self._fast_close(sock, sock.getpeername())
                    #self.close(sock)

    def release(self):
        for sock in self.connection:
            self._remove(sock, sock.getpeername())
            sock.close()

        self._my_socket.close()

    def is_conn(self, addr: Addr) -> bool:
        return addr in self.sockets

    def conn(self, addr: Addr):
        self._conn_que.append(addr)

    def send(self, sock: socket.socket, data: bytes):
        self._output_stream[sock].append(data)

    def send_by_addr(self, addr: Addr, data: bytes):
        self.send(self.sockets[addr], data)

    def recv(self, sock: socket.socket) -> bytes | None:
        if not self._input_stream[sock]:
            return None
        return self._input_stream[sock].popleft()

    def recv_by_addr(self, addr: Addr) -> bytes | None:
        return self.recv(self.sockets[addr])

    def pick(self, sock: socket.socket) -> bytes | None:
        if not self._input_stream[sock]:
            return None
        return self._input_stream[sock][0]

    def pcik(self, addr: Addr) -> bytes | None:
        self.pick(self.sockets[addr])

    def close(self, sock: socket.socket):
        self._disconn.append(sock)

    def close_by_addr(self, addr: Addr):
        self.close(self.sockets[addr])
