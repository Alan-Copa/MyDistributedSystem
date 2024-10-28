import socket
import threading
from template_pb2 import Message, FastHandshake

def split_buffer_to_messages(buffer):
    messages = []
    index = 0

    while index < len(buffer):
        # Look for the start of a new message, assuming it starts with '\x08'
        if buffer[index] == 0x08:
            # If we are not at the start of the buffer, consider everything before as a message
            if index > 0:
                messages.append(current_message)
            
            # Start a new message
            current_message = bytearray()
        
        # Add the current byte to the current message
        current_message.append(buffer[index])
        
        # Move to the next byte
        index += 1
    
    # Append the last collected message
    if current_message:
        messages.append(current_message)
    
    return messages


def send_message(conn, m):
    serialized = m.SerializeToString()
    conn.sendall(len(serialized).to_bytes(4, byteorder="big"))
    conn.sendall(serialized)


def receive_message(conn, m):
    msg = m()
    size = int.from_bytes(conn.recv(4), byteorder="big")
    data = conn.recv(size)
    msg.ParseFromString(data)
    return msg


def handler_messages(client_socket):
    # buffer = b""
    while True:
        try:
            # Receive incoming data from the server
            # data = client_socket.recv(1024)
            data = receive_message(client_socket, Message)
            if not data:
                break
            
            # print(f"Received data: {data}")
            print(f"[{data.fr}]: {data.msg}")

            # # split the buffer into messages
            # # raw_messages = split_buffer_to_messages(data)
            # raw_messages = [data]
            # print(f"Messages: {raw_messages}")
            # # work with the messages
            # # messages = [bytes(message) for message in raw_messages
            # # print(f"Messages: {messages}")
            # messages = raw_messages

            # # Process each message from the buffer
            # for queued_message in messages:
            #     # Try to deserialize a Message object from the buffer
            #     message = Message()

            #     try:
            #         message.ParseFromString(queued_message)
            #         # Print out the message
            #         print(f"[{message.fr}]: {message.msg}")

            #         # Remove the processed message from the buffer
            #         messages.remove(queued_message)

            #     except Exception as e:
            #         # If there's an error parsing, wait for more data
            #         break
                
        except Exception as e:
            print(f"[ERROR] Connection lost. {e}")
            break

def start_client(server_ip='127.0.0.1', server_port=8080, desired_id=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Perform Fast Handshake with the desired ID
    if desired_id is not None:
        handshake = FastHandshake()
        # handshake.id = desired_id
        # handshake.error = False  # Indicating no error initially
        # client_socket.sendall(handshake.SerializeToString())
        send_message(client_socket, handshake)

        # Wait for server response on whether the ID was accepted
        # response = client_socket.recv(1024)
        # server_handshake = FastHandshake()
        # server_handshake.ParseFromString(response)
        server_handshake = receive_message(client_socket, FastHandshake)

        if server_handshake.error:
            print(f"[SERVER] Requested ID {desired_id} is already in use.")
            print(f"[SERVER] Assigned new ID: {server_handshake.id}")
            client_id = server_handshake.id
        else:
            client_id = desired_id
            print(f"[SERVER] Successfully connected with ID {client_id}")

    # Start a thread to listen for incoming messages
    receive_thread = threading.Thread(target=handler_messages, args=(client_socket,))
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
                    # client_socket.sendall(msg.SerializeToString())

                    send_message(client_socket, msg)
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