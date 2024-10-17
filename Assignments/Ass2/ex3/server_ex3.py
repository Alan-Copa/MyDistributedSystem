import socket
import threading
import message_pb2

server_id = 5657 # Assign a unique ID for the server
clients = {} # Dictionary to store client connections
clients_lock = threading.Lock() # Lock to protect the clients dictionary
client_id_counter = 1 # Initialize a global counter to assign integer IDs

# Function to generate a simple integer client ID
def generate_client_id():
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1
    return client_id

# Function to safely update and access the number of connected clients
def get_num_connected_clients():
    with clients_lock:
        return len(clients)

# Function for each thread to handle the client connection
def handle_client(conn, addr, client_id):
    print(f"Client {addr} connected.")
    
    # Send a handshake message to the client using the new protobuf format
    try:
        handshake_message = message_pb2.Handshake()
        handshake_message.id = client_id
        handshake_message.error = False

        conn.send(handshake_message.SerializeToString()) # Send the handshake message in protobuf format

    except Exception as e:
        # If an error occurs, send an error handshake message and close the connection
        print(f"Error during handshake with client {addr}: {e}")
        handshake_message = message_pb2.Handshake()
        handshake_message.id = client_id
        handshake_message.error = True
        conn.send(handshake_message.SerializeToString())
        conn.close()
        return

    with clients_lock:
        clients[client_id] = {'conn': conn, 'addr': addr}

    try:
        with conn:
            while True:
                try:
                    # Check if the client has sent data
                    data = conn.recv(1024)

                    if not data:
                        # If no data is received, assume the connection is lost
                        if is_connection_alive(conn):
                            continue # Connection is alive, continue the loop
                        else:
                            print(f"Client {client_id} connection lost.")
                            break

                    # Deserialize the received protobuf message
                    chat_message = message_pb2.ChatMessage()
                    chat_message.ParseFromString(data)

                    if chat_message.msg.lower() == "end":
                        print(f"Client {client_id} sent 'end' - closing connection.")
                        break

                    print(f"Client {chat_message.from_} to {chat_message.to}: {chat_message.msg}")
                    conn.send(data) # Echo message back to the client

                except (ConnectionResetError, BrokenPipeError, KeyboardInterrupt):
                    # Handle abrupt disconnections (e.g., Ctrl+C on the client side)
                    print(f"Client {client_id} abruptly disconnected.")
                    break

    except OSError:
        pass

    finally:
        # Remove client from the clients dictionary and close connection
        with clients_lock:
            if client_id in clients:
                del clients[client_id]
        print(f"Connection with client {client_id} closed.")
        conn.close()

# Function to check if the connection is alive by sending a small probe
def is_connection_alive(conn):
    try:
        # check if the connection is alive 
        data = conn.recv(1024, socket.MSG_PEEK)
        return bool(data) # If there's data, the connection is alive
    except (ConnectionResetError, BrokenPipeError, OSError):
        return False

# Function to handle server operator commands
def server_operator():
    while True:
        command = input("Operator: ").strip().lower()
        if command == "num users":
            num_users = get_num_connected_clients()
            print(f"Number of connected clients: {num_users}")

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} (ID: {server_id}) started on port {port}\n")

    # Start the server operator thread
    operator_thread = threading.Thread(target=server_operator, daemon=True)
    operator_thread.start()

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen()
        print("Waiting for clients...\n")

        while True:
            try:
                conn, addr = s.accept()
                with clients_lock:
                    client_id = generate_client_id()
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
                    client_thread.start()
            except socket.error:
                break

    print(f"Server {server_name} has shut down.")

if __name__ == "__main__":
    main()