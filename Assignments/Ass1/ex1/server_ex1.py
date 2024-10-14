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
                # if message.lower() == "end":
                #     print(f"Client {addr} requested to close the connection.\n")
                #     break
                
                if data:
                    print(f"Client: {message}")
                    break # Exit the loop: remove if Bonus "end" is implemented
        
        print(f"Connection to {server_name} closed")

if __name__ == "__main__":
    main()
