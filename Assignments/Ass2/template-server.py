import socket
from sys import argv
from threading import Thread


def handle_client(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            print(f"Received: {data.decode()}")
            if data == b"exit":
                break
            conn.sendall(data)
        print("Closing connection to {addr}")


def main():
    try:
        port = int(argv[1])
    except:
        port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        print(f"Server started on port {port}")
        print("Waiting for a client...")
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                Thread(target=handle_client, args=(conn, addr)).start()
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
