import socket
import threading

# Global variable to keep track of the number of connected clients
n_connected_clients = 0
n_connected_clients_lock = threading.Lock() # Lock for thread safety

# Function to safely update the number of connected clients
def update_n_connected_clients(update):
    global n_connected_clients
    with n_connected_clients_lock:
        n_connected_clients += update

# Function for each thread to handle the client connection
def handle_client(conn, addr):
    print(f"Client {addr} connected.")
    update_n_connected_clients(1)

    try:
        with conn:
            while True:
                try:
                    data = conn.recv(1024).decode().strip()

                    if not data:
                        # Check if the connection is still alive
                        if is_connection_alive(conn):
                            continue # Connection is alive, continue the loop
                        else:
                            print(f"Client {addr} connection lost.")
                            break

                    if data.lower() == "end":
                        print(f"Client {addr} sent 'end' - closing connection.")
                        conn.send("Goodbye!\n".encode())
                        break

                    print(f"Client {addr}: {data}")
                    conn.send(f"{data}\n".encode())
                
                except (ConnectionResetError, BrokenPipeError, KeyboardInterrupt):
                    print(f"Client {addr} abruptly disconnected.")
                    break  

    except OSError:
        pass

    finally:
        update_n_connected_clients(-1)
        print(f"Connection with client {addr} closed.")
        conn.close()

# Function to check if the connection is alive by sending a small probe
def is_connection_alive(conn):
    try:
        # Use 'peek' to check if the connection is alive without consuming the data
        data = conn.recv(1024, socket.MSG_PEEK)
        return bool(data) # If there's data, the connection is alive
    except (ConnectionResetError, BrokenPipeError, OSError):
        return False # Connection is lost

# Function to handle server operator commands
def server_operator():
    print("Server operator started. Type 'num users' to see the number of connected clients.")
    while True:
        print("Operator: ", end='', flush=True)
        command = input().strip().lower()
        if command == "num users":
            with n_connected_clients_lock:
                print(f"Number of connected clients: {n_connected_clients}")

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} started on port {port}\n")

    # Start the server operator thread
    operator_thread = threading.Thread(target=server_operator, daemon=True)
    operator_thread.start()

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# Avoid "address already in use" error
        s.bind(("0.0.0.0", port))
        s.listen()
        s.settimeout(1.0) # Set a timeout for accepting new connections

        while True:
            try:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
            except socket.timeout:
                continue
            except socket.error:
                break # If shutdown, stop accepting new clients

    print(f"Server {server_name} has shut down.")

if __name__ == "__main__":
    main()