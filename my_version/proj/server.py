import socket
import threading
import uuid
from tabulate import tabulate  # External library for displaying tables, you can install via pip

# Global variables
n_connected_clients = 0
n_connected_clients_lock = threading.Lock()  # Lock for thread safety
clients = {}  # Dictionary to store client IDs and their details
clients_lock = threading.Lock()  # Lock to protect the clients dictionary

# Function to safely update the number of connected clients
def update_n_connected_clients(update):
    global n_connected_clients
    with n_connected_clients_lock:
        n_connected_clients += update

# Function to generate a unique client ID
def generate_client_id():
    return str(uuid.uuid4())  # Generate a random UUID for each client

# Function for each thread to handle the client connection
def handle_client(conn, addr, client_id):
    try:
        print(f"Client {client_id} ({addr}) connected.")
        update_n_connected_clients(1)  # Increase count when a client connects

        with clients_lock:  # Lock the clients dictionary when updating
            clients[client_id] = {'conn': conn, 'addr': addr}  # Store the client details

        with conn:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    continue
                if data.lower() == "end":
                    print(f"Client {client_id} sent 'end' - closing connection.")
                    conn.send("Goodbye!\n".encode())
                    break
                print(f"Client {client_id}: {data}")
                conn.send(f"{data}\n".encode())
    except OSError as e:
        print(f"Error handling client {client_id}: {e}")
    finally:
        # Ensure the connection is properly closed and removed from the clients dictionary
        print(f"Connection with client {client_id} closed.")
        update_n_connected_clients(-1)  # Decrease count when client disconnects
        
        with clients_lock:
            if client_id in clients:
                del clients[client_id]  # Remove the client from the dictionary

# Function to handle server operator commands
def server_operator(shutdown_event):
    while not shutdown_event.is_set():
        command = input("Operator: ").strip().lower()
        if command == "clients -n":
            with n_connected_clients_lock:
                print(f"Number of connected clients: {n_connected_clients}")
        elif command == "clients -l":
            list_clients()  # Display the list of connected clients
        elif command.startswith("disconnect"):
            _, client_id = command.split()
            disconnect_client(client_id)
        elif command == "shutdown":
            print("Shutting down the server...")
            graceful_shutdown()
            shutdown_event.set()  # Trigger the shutdown event to stop the server
            break

# Function to list all connected clients in a tabular format
def list_clients():
    with clients_lock:
        if not clients:
            print("No clients are currently connected.")
        else:
            table = []
            for client_id, info in clients.items():
                addr = info['addr']
                table.append([client_id, addr[0], addr[1]])  # [Client ID, IP, Port]
            print(tabulate(table, headers=["Client ID", "IP", "Port"]))

# Function to disconnect a client by their unique ID
def disconnect_client(client_id):
    with clients_lock:  # Lock the clients dictionary when accessing it
        if client_id in clients:
            conn = clients[client_id]['conn']
            conn.send("You have been disconnected by the server operator.\n".encode())
            conn.close()  # Close the client's connection
            print(f"Disconnected client {client_id}.")
        else:
            print(f"No client found with ID {client_id}.")

# Function for graceful shutdown
def graceful_shutdown():
    print("Disconnecting all clients...")
    with clients_lock:  # Lock the clients dictionary to prevent changes while shutting down
        for client_id, info in list(clients.items()):  # Use list to avoid dictionary size changes during iteration
            conn = info['conn']
            conn.send("Server is shutting down. You will be disconnected.\n".encode())
            conn.close()
            print(f"Disconnected client {client_id}.")
        clients.clear()  # Clear the clients dictionary
    print("All clients disconnected.")

def main():
    server_name = "CopaServer"
    port = 8080
    shutdown_event = threading.Event()  # Event to signal server shutdown

    print(f"{server_name} started on port {port}\n")

    # Start the server operator thread
    operator_thread = threading.Thread(target=server_operator, args=(shutdown_event,), daemon=True)
    operator_thread.start()

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set the SO_REUSEADDR option to avoid the "address already in use" error (Sometimes OS needs time to fully release the port)
        s.bind(("0.0.0.0", port))
        s.listen()  # Listen for incoming connections
        print("Waiting for clients...\n")

        while not shutdown_event.is_set():  # Run until shutdown event is triggered
            try:
                s.settimeout(1.0)  # Set a timeout for accepting new connections
                conn, addr = s.accept()  # Accept a new connection
                with clients_lock:  # Prevent accepting new connections during shutdown
                    if shutdown_event.is_set():
                        conn.close()  # Immediately close the connection if shutting down
                        break
                    client_id = generate_client_id()  # Generate a unique ID for the client
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
                    client_thread.start()
            except socket.timeout:
                continue  # Timeout hit, check shutdown_event again
            except socket.error:
                break  # If the server is shut down, exit the loop

    print("Server has shut down.")

if __name__ == "__main__":
    main()