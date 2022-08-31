from argparse import ArgumentParser

from src.daemon import Daemon


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--folder', default=None, type=str, help='folder with images for node')
    parser.add_argument('-p', '--port', default=9000, type=int, help='port to start the process')
    parser.add_argument('-c', '--connect', default=None, type=int, help='port to connect the peer')
    args = parser.parse_args()
    
    d = None
    if args.connect is not None:
        d = Daemon(("localhost", args.port), connect=("localhost", args.connect), folder=args.folder)
    else:
        d = Daemon(("localhost", args.port), folder=args.folder)

    d.connect()
