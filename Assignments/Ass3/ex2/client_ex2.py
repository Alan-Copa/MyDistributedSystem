import socket
import threading
from threading import Thread
from template_pb2 import Message, FastHandshake

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


def handler_messages_in(client_socket):
    while True:
        try:
            # Receive incoming data from the server
            # data = client_socket.recv(1024)
            data = receive_message(client_socket, Message)
            if not data:
                break
            
            print(f"[{data.fr}]: {data.msg}")

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

def handler_messages_out(client_socket, client_id=None):
    while True:
        try:
            # Get input from the user (message format: [id] [msg])
            message = input()
            if message.lower() == 'end':
                break
            if message:
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


def start_client(server_ip='127.0.0.1', server_port=8080, desired_id=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Perform Fast Handshake with the desired ID
    if desired_id is not None:
        handshake = FastHandshake(id=desired_id, error=False)
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
    receive_thread = Thread(target=handler_messages_in, args=(client_socket,))
    receive_thread.start()
    out_tread = Thread(target=handler_messages_out, args=(client_socket, client_id))
    out_tread.start()

    # Wait for the threads to finish
    receive_thread.join()
    out_tread.join()

    

    print("Connected to the server. You can start sending messages.")
    print("Message format: [id] [msg]")

    # Close the socket before exiting
    client_socket.close()
    print("Disconnected from the server.")

if __name__ == "__main__":
    # Example: The desired ID must be passed when starting the client
    desired_id = int(input("Enter your desired ID: "))
    start_client(desired_id=desired_id)