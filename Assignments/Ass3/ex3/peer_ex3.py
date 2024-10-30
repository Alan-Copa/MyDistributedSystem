from sys import argv
from threading import Thread
import socket
import template_pb2
from template_pb2 import Message, FastHandshake
from snowflake import derive_id  

class Peer:
    def __init__(self, my_ip, my_port, peer_id=None, connected_peers=None):
        self.my_ip = my_ip
        self.my_port = my_port
        self.peer_id = peer_id
        self.connected_peers = connected_peers if connected_peers else []
        self.connections = {} # Sockets to connected peers

    def run(self):
        # Listen for new connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.my_ip, self.my_port))
            s.listen()
            print(f"Peer {self.peer_id} listening on {self.my_ip}:{self.my_port}")
            
            # Connect to other peers
            for peer_ip, peer_port in self.connected_peers:
                print(f"Connecting to peer {peer_ip}:{peer_port}")
                # convert to int
                peer_port = int(peer_port)
                self.connect_to_peer(peer_ip, peer_port)

            # Start the thread for handling outgoing messages
            Thread(target=self.handle_out_m, daemon=True).start()

            # Accept new connections from peers
            while True:
                conn, addr = s.accept()
                # Start the handler thread for managing incoming and outgoing messages
                Thread(target=self.handle_peer, args=(conn, addr)).start()


    def handle_out_m(self):
        while True:
            try:
                # Get input from the user (message format: [id] [msg])
                print("Enter message format: [id] [msg]")
                message = input()
                if message.lower() == 'end':
                    break
                if message:
                    # Parse the input to extract recipient ID and message
                    recipient_id_str, msg_content = message.split(' ', 1)
                    print(f"recipient_id_str: {recipient_id_str}")
                    print(f"msg_content: {msg_content}")
                    try:
                        recipient_id = int(recipient_id_str)
                        # Create a Message object to send
                        msg = Message()
                        msg.fr = self.peer_id
                        msg.msg = msg_content
                        msg.to = recipient_id_str
                        print(f"Message sent {msg}")
                        self.send_message(msg)

                    except ValueError:
                        print("[ERROR] Invalid recipient ID.")
                else:
                    print("[ERROR] Invalid message format. Use '[id] [msg]'.")
            except:
                break

    def handle_peer(self, conn, addr):
        while True:
            try:
                msg = self.receive_message(conn)
                if msg.to == self.peer_id:
                    print(f"Message received: {msg.msg}")
                else:
                    print(f"Forwarding message to {msg.to}")
                    self.send_message(msg)
            except:
                break
        conn.close() # ????

    def connect_to_peer(self, peer_ip, peer_port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((peer_ip, peer_port))
        self.connections[(peer_ip, peer_port)] = conn
    
    def send_message(self, msg):
        """Send a serialized Protocol Buffer message to all connected peers."""
        print(f"Sending message: {msg.msg}")
        serialized = msg.SerializeToString()
        for conn in self.connections.values():
            conn.sendall(len(serialized).to_bytes(4, byteorder="big"))
            conn.sendall(serialized)

    def receive_message(self, conn):
        """Receive a serialized Protocol Buffer message from a peer."""
        size = int.from_bytes(conn.recv(4), byteorder="big")
        data = conn.recv(size)
        msg = template_pb2.Message()
        msg.ParseFromString(data)
        print(f"Message received: {msg.msg}")
        return msg

## End class Peer

def generate_id(my_ip):
    assigner_id = int.from_bytes(my_ip.encode(), byteorder='big')  # Use IP as assigner ID
    peer_id = derive_id(assigner_id)
    return peer_id
   
def main():
    try:
        my_ip, my_port = argv[1].split(":")
        my_port = int(my_port)
        desired_id = None
        
        # check if desired_id is provided
        if '--desired-id' in argv:
                desired_id_index = argv.index('--desired-id') + 1
                desired_id = int(argv[desired_id_index])
        
        #  get connected peers
        connected_peers = [tuple(peer.split(":")) for peer in argv[desired_id_index + 1:]]
    except:
        print("Usage: not correct")
        return

    if desired_id:
        peer_id = desired_id
    else:
        peer_id = generate_id(my_ip)
    
    peer = Peer(my_ip, my_port, peer_id, connected_peers)        
    print(f"[PEER STARTED] ID: {peer.peer_id}")
    peer.run()
    
if __name__ == "__main__":
    main()