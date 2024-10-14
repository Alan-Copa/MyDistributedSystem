import socket
from sys import argv


def main():
    try:
        port = int(argv[1])
    except:
        port = 8080

    print(f"Server started on port {port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        print("Waiting for a client...")
        # Q: What shall we put here?
        print("Closing connection")


if __name__ == "__main__":
    main()
