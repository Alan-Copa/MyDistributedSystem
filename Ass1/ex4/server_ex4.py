import socket
import threading

# Global variable to keep track of the number of connected clients
n_connected_clients = 0

# function to update the number of connected clients
def update_n_connected_clients(update):
    global n_connected_clients
    n_connected_clients += update
    print(f"Number of connected clients: {n_connected_clients}")

# Function for each thread to handle the client connection
def handle_client(conn, addr):
    print(f"Client {addr} connected.")
    with conn:
        while True:
            data = conn.recv(1024).decode().strip()
            # Ignore empty messages
            if not data:
                continue
            # Close the connection if the client sends 'end'
            if data.lower() == "end":
                print(f"Client {addr} sent 'end' - closing connection.")
                conn.send("Goodbye!\n".encode())
                # update_n_connected_clients(-1)
                break
            # Echo the message back to the client
            if data:
                print(f"Client {addr}: {data}")
                conn.send(f"{data}\n".encode())
    print(f"Connection with client {addr} closed.")
    update_n_connected_clients(-1)

def main():
    server_name = "CopaServer"
    port = 8080

    print(f"{server_name} started on port {port}\n")
    update_n_connected_clients(0)

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen()  # Listen for incoming connections
        print("Waiting for clients...\n")

        while True:
            conn, addr = s.accept()  # Accept a new connection
            # Create a thread to handle each client connection
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            update_n_connected_clients(1)

if __name__ == "__main__":
    main()

# Other possibilities:
# Asynchronous I/O: managing multiple connections at once with only a thread
# better for handling many clients.
# in the code: use async and await 