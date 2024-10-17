import socket
import message_pb2

def init_client():
    host = '127.0.0.1'
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Receive the handshake message from the server
        data = client_socket.recv(1024)
        handshake_message = message_pb2.Handshake()
        handshake_message.ParseFromString(data)

        if handshake_message.error:
            print("Handshake failed. Server reported an error.")
            return

        client_id = handshake_message.id
        print(f"Connected to the server with ID: {client_id}")
        print("Type your messages. Type 'end' to close the connection.")

        while True:
            message = input("You: ")

            if not message.strip():
                print("Empty messages are not allowed. Please enter a valid message.\n")
                continue

            chat_message = message_pb2.ChatMessage()
            chat_message.from_ = client_id  # Use the client ID received from the handshake
            # chat_message.recipient = server_id  # Set the recipient to the server ID received earlier
            chat_message.msg = message

            # Serialize the message and send it to the server
            serialized_message = chat_message.SerializeToString()
            client_socket.sendall(serialized_message)
            
            data = client_socket.recv(1024)
            if data:
                # Deserialize the protobuf message
                received_message = message_pb2.ChatMessage()
                received_message.ParseFromString(data)

                if received_message.msg == "Server is shutting down. Goodbye!":
                    print("The server has shut down. Disconnecting client.")
                    break  # Break the loop and close the client connection
                
                print(f"Server echoed: {received_message.msg}")

            # end command to terminate the connection
            if message.lower() == 'end':
                print("Closing client connection.")
                break

if __name__ == "__main__":
    init_client()