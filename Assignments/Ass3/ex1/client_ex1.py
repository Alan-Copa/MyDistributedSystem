import socket
from sys import argv
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
            msg = receive_message(client_socket, Message)
            print(f"[{msg.fr}]: {msg.msg}")
        except Exception as e:
            print(f"[ERROR] Connection lost: {e}")
            break

def start_client(server_ip='127.0.0.1', server_port=8080, desired_id=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))
        
        # Perform Fast Handshake
        handshake = FastHandshake(id=desired_id if desired_id else 0, error=False)
        send_message(client_socket, handshake)
        
        # Receive server response to handshake
        response = receive_message(client_socket, FastHandshake)
        client_id = response.id
        print(f"Connected as client {client_id}")

        # Start thread to handle incoming messages
        Thread(target=handler_messages_in, args=(client_socket,), daemon=True).start()

        print("You can start sending messages.")
        print("Message format: [id] [msg]")

        while True:
            user_input = input()
            if user_input.lower() == "end":
                break
            try:
                # Parse input to get recipient ID and message content
                recipient_id_str, msg_content = user_input.split(" ", 1)
                recipient_id = int(recipient_id_str)

                # Create and send the message using template's send_message
                message = Message(fr=client_id, to=recipient_id, msg=msg_content)
                send_message(client_socket, message)
            except ValueError:
                print("Invalid format. Use: [id] [msg]")
            except Exception as e:
                print(f"[ERROR] {e}")
                break

        print("Disconnected from the server.")

if __name__ == "__main__":
    desired_id = int(input("Enter your desired ID: "))
    start_client(desired_id=desired_id)