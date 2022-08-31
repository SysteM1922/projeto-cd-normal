import pickle
import socket

class Protocol:

    @staticmethod
    def recv(conn:socket.socket):
        size = conn.recv(8)
        if size:
            size = int.from_bytes(size, "big")
            data = conn.recv(size)

            return pickle.loads(data)
        return None

    @staticmethod
    def send(conn, msg):
        m = pickle.dumps(msg)
        return conn.send(len(m).to_bytes(8, "big") + m)

    @staticmethod
    def send_join(conn, connect):
        Protocol.send(conn, {"command": "JOIN", "args": {"address": connect}})

    @staticmethod
    def send_sync(conn, addr):
        Protocol.send(conn, {"command": "SYNC", "args": {"address": addr}})

    @staticmethod
    def send_register_client(conn, addr):
        Protocol.send(conn, {"command": "REGISTER_CLIENT", "args": {"address": addr}})

    @staticmethod
    def send_get_all_images(conn, addr):
        Protocol.send(conn, {"command": "GET_ALL_IMAGES", "args": {"address": addr}})

