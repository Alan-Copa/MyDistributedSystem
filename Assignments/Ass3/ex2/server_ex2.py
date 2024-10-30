import socket
import threading
from threading import Thread
from sys import argv
from template_pb2 import Message, FastHandshake

CLIENTS = {} # Dictionary to store connected clients {client_id: connection}
MESSAGE_QUEUE = {} # Dictionary to store messages for offline clients {client_id: [messages]}
LAST_ID = 0  # Counter to track the last assigned ID

def assign_new_id():
    global LAST_ID
    LAST_ID += 1
    while LAST_ID in CLIENTS:
        LAST_ID += 1
    return LAST_ID


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


def handle_client(conn: socket.socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    # Receive the initial handshake from the client to determine the desired ID
    handshake = receive_message(conn, FastHandshake)
    print(f"handshake id  {handshake.id}")
    
    desired_id = handshake.id
    if desired_id in CLIENTS or desired_id <= 0:
        # ID is already in use or invalid, assign a new standard ID
        assigned_id = assign_new_id()
        print(f"[HANDSHAKE] ID {desired_id} is invalid or already in use. Assigned new ID: {assigned_id}.")
        
        # Send a response with the new ID (error=True, but providing a new ID)
        response = FastHandshake(id=assigned_id, error=(desired_id != assigned_id))
        print(f"response {response}")
        send_message(conn, response)

        # Use the new assigned ID
        CLIENTS[assigned_id] = conn
        # Deliver any buffered messages
        deliver_buffered_messages(conn, assigned_id)
    else:
        # Accept the desired ID and add to connected clients
        CLIENTS[desired_id] = conn
        print(f"[HANDSHAKE] Client {desired_id} connected successfully.")
        
        # Send success response
        response = FastHandshake(id=desired_id, error=False)
        send_message(conn, response)
        
        # Deliver any buffered messages
        deliver_buffered_messages(conn, desired_id)

    try:
        with conn:
            while True:
                # Receive message from the client
                message_data = receive_message(conn, Message)
                if not message_data:
                    break

                recipient_id = message_data.to
                msg_content = message_data.msg
                
                # Check if the recipient is in the list of connected clients
                if recipient_id in CLIENTS:
                    # Forward the message to the intended recipient
                    recipient_socket = CLIENTS[recipient_id]
                    # recipient_socket.sendall(message_data)
                    send_message(recipient_socket, message_data)
                if msg_content == "end":
                    break
                else:
                    # Store the message for delivery when the client reconnects
                    if recipient_id not in MESSAGE_QUEUE:
                        MESSAGE_QUEUE[recipient_id] = []
                    # MESSAGE_QUEUE[recipient_id].append(message_data)
                    MESSAGE_QUEUE.setdefault(message_data.to, []).append(message_data)

                
    finally:
        # Remove client from the connected list when they disconnect
        conn.close()
        for client_id, sock in list(CLIENTS.items()):
            if sock == conn:
                del CLIENTS[client_id]
                print(f"[DISCONNECTED] Client {client_id} disconnected.")
                break

def deliver_buffered_messages(conn, client_id):
    if client_id in MESSAGE_QUEUE and MESSAGE_QUEUE[client_id]:
        print(f"[INFO] Delivering buffered messages to client {client_id}.")
        print(f"[INFO] {MESSAGE_QUEUE[client_id]} messages in the queue.")
        client_socket = CLIENTS[client_id]
        for message in MESSAGE_QUEUE[client_id]:
            print(f"[INFO] Delivering queud message: {message}")
            send_message(conn, message)
        # Clear the queue after delivering messages
        MESSAGE_QUEUE[client_id] = []
        print(f"[INFO] Qeue of client {client_id} cleared: {MESSAGE_QUEUE[client_id]}")

def loop_main(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            print(f"Server started on port {port}")
            print("Waiting for a client...")
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    Thread(target=handle_client, args=(conn, addr)).start()
                except KeyboardInterrupt:
                    break
    except:
        pass

def main():
    global CLIENTS

    try:
        port = int(argv[1])
    except:
        port = 8080

    loop = threading.Thread(target=loop_main, args=(port,))
    loop.daemon = True
    loop.start()

    while True:
        try:
            command = input("op> ").strip().lower()
        except:
            break

        if command == "num_users":
            print(f"Number of users: {len(CLIENTS)}")
        else:
            print("Invalid command")
            print("Available commands:")
            print("- num_users: Get the number of connected users")

if __name__ == "__main__":
    main()