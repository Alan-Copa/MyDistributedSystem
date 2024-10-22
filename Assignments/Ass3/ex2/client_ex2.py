import socket
import threading
from template_pb2 import Message, FastHandshake

def receive_messages(client_socket):
    buffer = b""
    while True:
        try:
            # Receive incoming data from the server
            data = client_socket.recv(1024)
            if not data:
                break
            
            # Add data to buffer
            buffer += data

            # Process each message from the buffer
            while len(buffer) > 0:
                # Try to deserialize a Message object from the buffer
                message = Message()

                try:
                    message.ParseFromString(buffer)
                    # Print out the message
                    print(f"[{message.fr}]: {message.msg}")

                    # Remove the processed message from the buffer
                    buffer = buffer[message.ByteSize():]

                except Exception as e:
                    # If there's an error parsing, wait for more data
                    break
                
        except Exception as e:
            print(f"[ERROR] Connection lost. {e}")
            break

def start_client(server_ip='127.0.0.1', server_port=8080, desired_id=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Perform Fast Handshake with the desired ID
    if desired_id is not None:
        handshake = FastHandshake()
        handshake.id = desired_id
        handshake.error = False  # Indicating no error initially
        client_socket.send(handshake.SerializeToString())

        # Wait for server response on whether the ID was accepted
        response = client_socket.recv(1024)
        server_handshake = FastHandshake()
        server_handshake.ParseFromString(response)

        if server_handshake.error:
            print(f"[SERVER] Requested ID {desired_id} is already in use.")
            print(f"[SERVER] Assigned new ID: {server_handshake.id}")
            client_id = server_handshake.id
        else:
            client_id = desired_id
            print(f"[SERVER] Successfully connected with ID {client_id}")

    # Start a thread to listen for incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    print("Connected to the server. You can start sending messages.")
    print("Message format: [id] [msg]")

    while True:
        try:
            # Get input from the user (message format: [id] [msg])
            message = input()
            if message.lower() == 'end':
                break
            if ' ' in message:
                # Parse the input to extract recipient ID and message
                recipient_id_str, msg_content = message.split(' ', 1)
                try:
                    recipient_id = int(recipient_id_str)

                    # Create a Message object to send
                    msg = Message()
                    msg.fr = client_id if client_id else 0  # Use the chosen ID
                    msg.to = recipient_id
                    msg.msg = msg_content

                    # Serialize the Message and send it
                    client_socket.send(msg.SerializeToString())
                except ValueError:
                    print("[ERROR] Invalid recipient ID.")
            else:
                print("[ERROR] Invalid message format. Use '[id] [msg]'.")
        except KeyboardInterrupt:
            break

    # Close the socket before exiting
    client_socket.close()
    print("Disconnected from the server.")

if __name__ == "__main__":
    # Example: The desired ID must be passed when starting the client
    desired_id = int(input("Enter your desired ID: "))
    start_client(desired_id=desired_id)