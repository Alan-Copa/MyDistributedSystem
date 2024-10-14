import socket
import threading
import random
import time
from sys import argv

# Function for each thread to execute
def thread_task(conn):
    thread_id = threading.get_ident()  # Get the system-assigned thread ID
    greeting_message = f"Hi, I'm thread {thread_id}\n"
    conn.send(greeting_message.encode())  # Send greeting to the client
    
    # Sleep for a random time between 1 and 5 seconds
    sleep_time = random.randint(1, 5)
    time.sleep(sleep_time)
    
    farewell_message = f"Thread {thread_id} says goodbye after sleeping for {sleep_time} seconds.\n"
    conn.send(farewell_message.encode())  # Send farewell to the client

def main():
    server_name = "CopaServer"
    try:
        port = int(argv[1])
    except:
        port = 8080

    print(f"{server_name} started on port {port}\n")

    # Create a socket and bind it to the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen()  # Listen for incoming connections
        print("Waiting for a client...\n")

        conn, addr = s.accept()  # Accept a new connection
        print(f"Connected by client {addr}\n")

        # Use 'with' to automatically handle the connection lifecycle
        with conn:
            threads = []
            
            # Spawn 3 threads that will interact with the client
            for _ in range(3):
                thread = threading.Thread(target=thread_task, args=(conn,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # The connection will be closed automatically by the 'with' block
            print(f"Connection to {server_name} closed")

if __name__ == "__main__":
    main()