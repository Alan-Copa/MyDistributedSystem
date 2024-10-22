import socket
import threading
from sys import argv
from template_pb2 import Message, FastHandshake

CLIENTS = {}  # Dictionary to store connected clients {client_id: connection}
LAST_ID = 0   # Counter to track the last assigned ID

def assign_new_id():
    global LAST_ID
    LAST_ID += 1
    # control that the new id isn't already in use
    while LAST_ID in CLIENTS:
        LAST_ID += 1
    return LAST_ID

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    
    # Receive the initial handshake from the client to determine the desired ID
    data = client_socket.recv(1024)
    handshake = FastHandshake()
    handshake.ParseFromString(data)
    
    desired_id = handshake.id
    if desired_id in CLIENTS or desired_id <= 0:
        # ID is already in use or invalid, assign a new standard ID
        assigned_id = assign_new_id()
        print(f"[HANDSHAKE] ID {desired_id} is invalid or already in use. Assigned new ID: {assigned_id}.")
        
        # Send a response with the new ID (error=True, but providing a new ID)
        response = FastHandshake()
        response.id = assigned_id
        response.error = True
        client_socket.send(response.SerializeToString())

        # Use the new assigned ID
        CLIENTS[assigned_id] = client_socket
    else:
        # Accept the desired ID and add to connected clients
        CLIENTS[desired_id] = client_socket
        print(f"[HANDSHAKE] Client {desired_id} connected successfully.")
        
        # Send success response
        response = FastHandshake()
        response.id = desired_id
        response.error = False
        client_socket.send(response.SerializeToString())

    try:
        while True:
            # Receive message from the client
            message_data = client_socket.recv(1024)
            if not message_data:
                break

            # Deserialize the data as a Message object
            message = Message()
            message.ParseFromString(message_data)
            recipient_id = message.to
            msg_content = message.msg
            
            # Check if the recipient is in the list of connected clients
            if recipient_id in CLIENTS:
                # Forward the message to the intended recipient
                recipient_socket = CLIENTS[recipient_id]
                recipient_socket.send(message_data)
            else:
                print(f"[INFO] Message to non-existent client {recipient_id} dropped.")
                
    finally:
        # Remove client from the connected list when they disconnect
        client_socket.close()
        for client_id, sock in list(CLIENTS.items()):
            if sock == client_socket:
                del CLIENTS[client_id]
                print(f"[DISCONNECTED] Client {client_id} disconnected.")
                break

def loop_main(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            print(f"Server started on port {port}")
            print("Waiting for a client...")
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=handle_client, args=(conn, addr)).start()
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