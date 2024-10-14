import socket
import threading

# Global variable to keep track of the number of connected clients
n_connected_clients = 0
n_connected_clients_lock = threading.Lock()  # Lock for thread safety
shutdown_event = threading.Event()  # Event to signal server shutdown
client_threads = []  # List to store all active client threads
clients = {}  # Dictionary to store client connections
clients_lock = threading.Lock()  # Lock to protect the clients dictionary

# Function to safely update the number of connected clients
def update_n_connected_clients(update):
    global n_connected_clients
    with n_connected_clients_lock:
        n_connected_clients += update

# Function for each thread to handle the client connection
def handle_client(conn, addr):
    print(f"Client {addr} connected.")
    update_n_connected_clients(1)
    
    # Add client to the clients dictionary
    with clients_lock:
        clients[addr] = conn

    with conn:
        while not shutdown_event.is_set():  # Check shutdown_event before handling client messages
            try:
                data = conn.recv(1024).decode().strip()
                if not data:
                    continue
                if data.lower() == "end":
                    print(f"Client {addr} sent 'end' - closing connection.")
                    conn.send("Goodbye!\n".encode())
                    break
                print(f"Client {addr}: {data}")
                conn.send(f"{data}\n".encode())
            except OSError:
                break  # Gracefully handle the client disconnection if connection is closed

    # Remove client from the clients dictionary and close connection
    with clients_lock:
        if addr in clients:
            del clients[addr]
    update_n_connected_clients(-1)
    conn.close()  # Ensure connection is closed

# Function to handle server operator commands
def server_operator():
    while not shutdown_event.is_set():
        print("Operator: ", end='', flush=True)  # Ensures "Operator:" is displayed
        command = input().strip().lower()
        if command == "num users":
            with n_connected_clients_lock:
                print(f"Number of connected clients: {n_connected_clients}")
        elif command == "exit":
            print("Shutting down the server...")
            graceful_shutdown()  # Call the graceful shutdown function
            shutdown_event.set()  # Trigger the shutdown event to stop the server
            break

# Graceful shutdown to inform all clients and close connections
def graceful_shutdown():
    print("Disconnecting all clients...")
    with clients_lock:
        for addr, conn in list(clients.items()):
            try:
                conn.sendall("Server is shutting down. Goodbye!\n".encode())
            except:
                pass
            conn.close()
            print(f"Disconnected client {addr}.")
        clients.clear()  # Clear the clients dictionary
    print("All clients disconnected.")

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} started on port {port}\n")

    # Start the server operator thread
    operator_thread = threading.Thread(target=server_operator, daemon=True)
    operator_thread.start()

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "address already in use" error
        s.bind(("0.0.0.0", port))
        s.listen()
        s.settimeout(1.0)  # Set a timeout for accepting new connections
        print("Waiting for clients...\n")

        while not shutdown_event.is_set():  # Check shutdown_event before accepting new connections
            try:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
                client_threads.append(client_thread)  # Track client threads
            except socket.timeout:
                continue  # Timeout hit, check shutdown_event again
            except socket.error:
                break  # If shutdown, stop accepting new clients

    # Wait for all client threads to finish
    for t in client_threads:
        t.join()  # Ensure all clients are disconnected before shutting down

    print(f"Server {server_name} has shut down.")

if __name__ == "__main__":
    main()