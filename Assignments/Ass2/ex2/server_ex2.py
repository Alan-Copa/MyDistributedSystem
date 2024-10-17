import socket
import threading
import message_pb2 # Import the generated protobuf class

server_id = 5657 # Assign a unique ID for the server
clients = {} # Dictionary to store client connections
clients_lock = threading.Lock() # Lock to protect the clients dictionary

# Function for each thread to handle the client connection
def handle_client(conn, addr, client_id):
    print(f"Client {addr} connected.")
    # Send the server ID and client ID to the client upon connection
    conn.send(f"Server: My ID {server_id}, Your ID: {client_id}\n".encode())

    with clients_lock:
        clients[client_id] = {'conn': conn, 'addr': addr} # Store the client details

    with conn:
        while True:
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

                # Log and send an echoed message back
                print(f"Client {chat_message.from_} to {chat_message.to}: {chat_message.msg}")
                
                # Prepare a response message from the server
                response_message = message_pb2.ChatMessage()
                response_message.from_ = server_id
                response_message.to = chat_message.from_ # Reply to the original sender
                response_message.msg = f"Server echoed: {chat_message.msg}"

                # Serialize the response and send it back to the client
                conn.send(response_message.SerializeToString())
            except OSError:
                break
    
    # Remove client from the clients dictionary and close connection
    with clients_lock:
        if client_id in clients:
            del clients[client_id]
    conn.close() # Ensure connection is closed
    print(f"Connection with client {client_id} closed.")

# Clientd IDs generator
client_id_counter = 1
def generate_client_id():
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1
    return client_id

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} (ID: {server_id}) started on port {port}\n")

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
            except socket.timeout:
                continue
            except socket.error:
                break

    print(f"Server {server_name} has shut down.")

if __name__ == "__main__":
    main()