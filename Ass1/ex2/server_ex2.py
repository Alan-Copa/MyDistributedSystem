import socket
from sys import argv

def main():
    server_name = "CopaServer"
    try:
        port = int(argv[1])
    except:
        port = 8080

    print(f"{server_name} started on port {port}\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        # Listen for incoming connections
        s.listen()
        print("Waiting for clients...\n")
        # Accept a connection
        conn, addr = s.accept()
        with conn:
            print(f"Connected by client {addr}\n")
            while True:
                data = conn.recv(1024)
                message = data.decode().strip()
                # Bonus: Terminate if "end" is received
                if message.lower() == "end":
                    print(f"Client {addr} requested to close the connection.\n")
                    # goodbye message to the client :)
                    conn.send("Goodbye!\n".encode())
                    break
                # Respond to the client with a hello message
                elif message.lower() == "hello":
                    conn.send("hello :)!\n".encode())
                # Echo the message back to the client
                elif data:
                    print(f"Client: {message}\n")
                    reply = f"{message}\n"
                    conn.send(reply.encode())
        
        print(f"Connection to {server_name} closed")

if __name__ == "__main__":
    main()