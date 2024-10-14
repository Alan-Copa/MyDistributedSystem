import socket
import threading
import message_pb2  # Import the generated protobuf class

server_id = 5657  # Assign a unique ID for the server
clients = {}  # Dictionary to store client connections
clients_lock = threading.Lock()  # Lock to protect the clients dictionary
shutdown_event = threading.Event()  # Event to signal server shutdown
client_id_counter = 1  # Initialize a global counter to assign integer IDs

# Function to generate a simple integer client ID
def generate_client_id():
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1  # Increment the counter for the next client
    return client_id  # Return the new client ID as an integer

# Function for each thread to handle the client connection
def handle_client(conn, addr, client_id):
    print(f"Client {addr} connected.")

    # Send a handshake message to the client using the new protobuf format
    try:
        handshake_message = message_pb2.Handshake()
        handshake_message.id = client_id
        handshake_message.error = False

        conn.send(handshake_message.SerializeToString())  # Send the handshake message in protobuf format

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
        clients[client_id] = {'conn': conn, 'addr': addr}  # Store the client details

    with conn:
        while not shutdown_event.is_set():  # Check shutdown_event before handling client messages  
            try:
                data = conn.recv(1024)
                if not data:
                    continue
                # Deserialize the protobuf message
                chat_message = message_pb2.ChatMessage()
                chat_message.ParseFromString(data)

                if chat_message.msg.lower() == "end":
                    print(f"Client {client_id} sent 'end' - closing connection.")
                    break

                print(f"Client {chat_message.sender} to {chat_message.recipient}: {chat_message.msg}")
                conn.send(data)  # Echo the serialized protobuf message back to the client
            except OSError:
                break   # Gracefully handle the client disconnection if connection is closed

    # Remove client from the clients dictionary and close connection
    with clients_lock:
        if client_id in clients:
            del clients[client_id]
    conn.close()  # Ensure connection is closed
    print(f"Connection with client {client_id} closed.")

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} (ID: {server_id}) started on port {port}\n")

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "address already in use" error
        s.bind(("0.0.0.0", port))
        s.listen()  # Listen for incoming connections
        print("Waiting for clients...\n")

        while not shutdown_event.is_set():  # Check shutdown_event before accepting new connections
            try:
                conn, addr = s.accept()
                with clients_lock:
                    if shutdown_event.is_set():
                        conn.close()
                        break
                    client_id = generate_client_id()  # Generate a unique integer ID for the client
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
                    client_thread.start()
            except socket.timeout:
                continue  # Timeout hit, check shutdown_event again
            except socket.error:
                break  # If shutdown, stop accepting new clients

    print(f"Server {server_name} has shut down.")

if __name__ == "__main__":
    main()