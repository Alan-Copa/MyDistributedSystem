import socket

def init_client():
    host = '127.0.0.1'
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        print("Connected to the server. Type your messages.")
        while True:
            # Take user input
            message = input("You: ")
            # Check if the message is empty
            if not message.strip():
                print("Empty messages are not allowed. Please enter a valid message.\n")
                continue
            # Send the message to the server
            client_socket.send(message.encode())
            # Server's reply
            data = client_socket.recv(1024).decode()
            if data:
                print(f"Server: {data}")
            # end command to terminate the connection
            if message.lower() == 'end':
                print("Closing client connection.") 
                break

if __name__ == "__main__":
    init_client()
