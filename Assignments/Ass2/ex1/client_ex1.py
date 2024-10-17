import socket

def init_client():
    host = '127.0.0.1'
    port = 8080

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print("Connected to the server. Type your messages. Type 'end' to close the connection.")
            
            while True:

                message = input("You: ")

                if not message.strip():
                    print("Empty messages are not allowed. Please enter a valid message.\n")
                    continue

                try:
                    client_socket.sendall(message.encode())
                except ConnectionResetError:
                    print("Server has closed the connection unexpectedly.")
                    break

                # end command to terminate the connection
                if message.lower() == 'end':
                    print("Closing client connection.") 
                    break

                # Receive the server's response and close the connection if the server has closed it
                data = client_socket.recv(1024).decode()
                if data:
                    print(f"Server: {data}")
                if "Goodbye" in data or "disconnected" in data.lower():
                    print("Server has closed the connection.")
                    break

    except ConnectionRefusedError:
        print("Unable to connect to the server. Please try again later.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    init_client()