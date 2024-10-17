import socket

def init_client():
    host = '127.0.0.1'
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print("Connected to the server. Type your messages. Type 'end' to close the connection.")
        
        while True:
            message = input("You: ")

            if not message.strip():
                print("Empty messages are not allowed. Please enter a valid message.\n")
                continue

            try:
                # Send message to the server
                client_socket.sendall(message.encode())
            except BrokenPipeError:
                print("Server has closed the connection. You have been disconnected.")
                break  # Exit the loop if the connection is closed

            # Receive server response
            try:
                data = client_socket.recv(1024).decode()
                if data:
                    print(f"Server: {data}")

                # Check if the server has disconnected the client
                if "disconnected" in data.lower():
                    print("You have been disconnected by the server operator.")
                    break

            except ConnectionResetError:
                print("Connection reset by server.")
                break  # Exit if the connection is forcibly reset by the server

            # end command to terminate the connection
            if message.lower() == 'end':
                print("Closing client connection.")
                break

if __name__ == "__main__":
    init_client()