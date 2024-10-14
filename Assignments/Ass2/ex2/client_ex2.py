import socket
import message_pb2  # Import the generated protobuf class

def init_client():
    host = '127.0.0.1'
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Receive the server ID when connecting
        server_id_message = client_socket.recv(1024).decode().strip()
        print(server_id_message)

        # Extract the server and client ID from the message
        server_id = int(server_id_message.split("My ID ")[1].split(",")[0].strip())
        client_id = server_id_message.split("Your ID:")[1].strip()

        print(f"Connected to server with ID: {server_id}")
        print(f"Your client ID: {client_id}")
        print("Type your messages. Type 'end' to close the connection.")

        while True:
            message = input("You: ")

            if not message.strip():
                print("Empty messages are not allowed. Please enter a valid message.\n")
                continue

            # Create a new ChatMessage object
            chat_message = message_pb2.ChatMessage()
            chat_message.sender = int(client_id)  # Use the client ID received from the server
            chat_message.recipient = server_id  # Set the recipient to the server ID received
            chat_message.msg = message

            # Serialize the message and send it to the server
            serialized_message = chat_message.SerializeToString()
            client_socket.send(serialized_message)
            
            data = client_socket.recv(1024)
            if data:
                # Deserialize the protobuf message
                received_message = message_pb2.ChatMessage()
                received_message.ParseFromString(data)
                print(f"Server: {received_message.msg}")

if __name__ == "__main__":
    init_client()