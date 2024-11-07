import socket
from sys import argv
from threading import Thread
from template_pb2 import Message, FastHandshake

CLIENTS = {}  # Dictionary to store connected clients {client_id: connection}
LAST_ID = 0   # Counter to track the last assigned ID

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

def assign_new_id():
    global LAST_ID
    LAST_ID += 1
    # Ensure the new ID isn’t already in use
    while LAST_ID in CLIENTS:
        LAST_ID += 1
    return LAST_ID

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    # Receive the initial handshake from the client to determine the desired ID
    handshake = receive_message(conn, FastHandshake)
    
    desired_id = handshake.id
    if desired_id in CLIENTS or desired_id <= 0:
        # ID is already in use or invalid, assign a new standard ID
        assigned_id = assign_new_id()
        print(f"[HANDSHAKE] ID {desired_id} is invalid or already in use. Assigned new ID: {assigned_id}.")
        
        # Send a response with the new ID (error=True, but providing a new ID)
        response = FastHandshake(id=assigned_id, error=(desired_id != assigned_id))
        send_message(conn, response)

        # Use the new assigned ID
        CLIENTS[assigned_id] = conn

    else:
        # Accept the desired ID and add to connected clients
        CLIENTS[desired_id] = conn
        print(f"[HANDSHAKE] Client {desired_id} connected successfully.")
        
        # Send success response
        response = FastHandshake(id=desired_id, error=False)
        send_message(conn, response)

    with conn:
        while True:
            try:
                # Receive message from the client
                msg = receive_message(conn, Message)
                print(f"Received: {msg.msg} from {msg.fr} to {msg.to}")

                if msg.msg == "end":
                    break  # Exit loop on "end" message

                # Check if recipient exists and forward message
                recipient_id = msg.to
                if recipient_id in CLIENTS:
                    send_message(CLIENTS[recipient_id], msg)
                else:
                    print(f"[INFO] Message to non-existent client {recipient_id} dropped.")
            except Exception as e:
                print(f"[ERROR] {e}")
                break
        
        print(f"Closing connection to #{id} {addr}")
        CLIENTS.pop(id, None)  # Remove client from list upon disconnect

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
                    Thread(target=handle_client, args=(conn, addr)).start()
                except KeyboardInterrupt:
                    break
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    global CLIENTS

    try:
        port = int(argv[1])
    except:
        port = 8080

    loop = Thread(target=loop_main, args=(port,))
    loop.daemon = True
    loop.start()

    while True:
        try:
            command = input("op> ").strip().lower()
        except KeyboardInterrupt:
            break

        if command == "num_users":
            print(f"Number of users: {len(CLIENTS)}")
        else:
            print("Invalid command")
            print("Available commands:")
            print("- num_users: Get the number of connected users")

if __name__ == "__main__":
    main()