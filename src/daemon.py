from optparse import Values
import selectors
import socket
import imagehash
import pickle
import time
import os

from PIL import Image
from .protocol import Protocol


class Daemon:
    def __init__(self, addr, connect=None, folder=None):
        self.addr = addr
        self.peers = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        self.sock.listen()

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)

        if connect is not None:
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            peer.connect(connect)
            Protocol.send_join(peer, self.addr)
            self.peers.append(peer)
            self.sel.register(peer, selectors.EVENT_READ, self.pop)

        self.client=None
        self.images = folder
        self.images_hash = {}
        self.duplicates()

    def accept(self, conn):
        sock, addr = conn.accept()
        self.sel.register(sock, selectors.EVENT_READ, self.read)

    def read(self, conn):
        msg = Protocol.recv(conn)
        if not msg:
            return

        print(msg)

        if msg == "__KEEPALIVE__":
            return

        command = msg["command"]
        args = msg["args"]

        if command == "JOIN":
            new_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_peer.connect(args["address"])
            if new_peer not in self.peers:
                for peer in self.peers:
                    Protocol.send_sync(peer, args["address"])
                    Protocol.send_sync(new_peer, peer.getpeername())

                self.peers.append(new_peer)
                self.sel.register(new_peer, selectors.EVENT_READ, self.pop)
        elif command == "SYNC":
            new_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_peer.connect(args["address"])
            self.peers.append(new_peer)
            self.sel.register(new_peer, selectors.EVENT_READ, self.pop)

        elif command == "REGISTER_CLIENT":
            self.client = (conn, args["address"])

        elif command == "GET_ALL_IMAGES":
            for hash in self.images_hash:
                pass


    def pop(self, conn):
        msg = Protocol.recv(conn)
        if not msg:
            self.peers.remove(conn)
            self.sel.unregister(conn)
            conn.close()

    def duplicates(self):
        for image in os.listdir(self.images):
            hash = imagehash.phash(Image.open(self.images+"/"+image))
            if hash in self.images_hash:
                self.images_hash[hash].append(self.images+"/"+image)
            else:
                self.images_hash[hash] = [self.images+"/"+image]
            
        for hash in self.images_hash:
            if len(self.images_hash[hash]) > 1:
                self.images_hash[hash]=sorted(self.images_hash[hash], key=lambda x: os.stat(x).st_size)
                size = len(self.images_hash[hash])
                while size > 1:
                    os.remove(self.images_hash[hash][-1])
                    self.images_hash[hash]=self.images_hash[hash].pop(-1)
                    size-=1


    def connect(self):
        while True:
            for key, _ in self.sel.select():
                callback = key.data
                callback(key.fileobj)
