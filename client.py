import socket
from src.protocol import Protocol

from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='port to start the process')
    parser.add_argument('-c', '--connect', type=int, help='port to connect the peer')
    args = parser.parse_args()

    addr=("localhost", args.port)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn.connect(("localhost", args.connect))
    Protocol.send_register_client(conn, addr)
    
    while True:
        sc = input("$ ")

        if sc.startswith("get "):
            file = sc.replace("get ", "")


        elif sc == "list":
            Protocol.send_get_all_images(conn, addr)
            # list all images
