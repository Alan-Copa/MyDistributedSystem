import socket
import threading
import random
import time
from sys import argv

# Function for each thread to execute
def thread_task(conn, id):
    # thread_id = threading.get_ident() # Get the system-assigned thread ID (useful if manual identifier is not provided)
    greeting_message = f"Hi, I'm thread {id}\n"
    conn.send(greeting_message.encode())
    
    sleep_time = random.randint(1, 10)
    time.sleep(sleep_time)
    
    farewell_message = f"Thread {id} slept for {sleep_time} seconds.\n"
    conn.send(farewell_message.encode())

def main():
    server_name = "CopaServer"
    try:
        port = int(argv[1])
    except:
        port = 8080

    print(f"{server_name} started on port {port}\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set the SO_REUSEADDR option to avoid the "address already in use" error (Sometimes OS needs time to fully release the port)
        s.bind(("0.0.0.0", port))
        s.listen()
        print("Waiting for a client...\n")
        # Accept a new connection
        conn, addr = s.accept()
        print(f"Connected by client {addr}\n")

        with conn:
            threads = []
            # Spawn 3 threads that will interact with the client and assign identifier
            for i in range(1,4):
                thread = threading.Thread(target=thread_task, args=(conn,i))
                threads.append(thread)
                thread.start()
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            print("All threads have completed their tasks, but keeping connection open...")

            # Keep the connection open after threads have finished
            while True:
                data = conn.recv(1024).decode().strip()
                 # Ignore empty messages
                if not data:
                    continue
                elif data.lower() == "end":
                    print("Client requested to close the connection.")
                    conn.send("Goodbye!\n".encode())
                    break
                # Echo the message back to the client
                conn.send(f"Server received: {data}\n".encode())

            print(f"Connection to {server_name} closed")

if __name__ == "__main__":
    main()