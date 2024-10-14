# Distributed Systems - Server with Operator Control

## Overview
This project implements a multi-client server for managing client connections using threading in Python. The server has a built-in operator interface that allows the server admin to interact with the server while it's running, offering several useful commands for managing and monitoring clients.

## Features
- **Multi-Client Support**: The server can handle multiple clients simultaneously using threads, allowing each client to connect and communicate independently.
- **Unique Client IDs**: Each client is assigned a random UUID upon connection. This ID is used for managing and identifying clients.
- **Server Operator Interface**: The operator can interact with the server through several commands, enabling client management and server monitoring in real-time.
- **Graceful Shutdown**: The server supports a graceful shutdown process, ensuring that all clients are disconnected properly before the server terminates.

## Operator Commands
- **`num users`**: Displays the current number of connected clients.
- **`list clients`**: Displays a table of all currently connected clients, including their unique ID, IP address, and port number.
- **`disconnect <client_id>`**: Disconnects the client with the specified unique client ID.
- **`shutdown`**: Initiates a graceful server shutdown, disconnecting all clients and stopping the server.

## How it Works
1. **Client Connection**: When a client connects to the server, they are assigned a unique UUID, which is used by the operator for managing the connection.
2. **Client Interaction**: Clients can send messages to the server. The server will echo back their messages. If the client sends `"end"`, they will be disconnected.
3. **Operator Management**: While the server is running, the operator can issue commands to see how many clients are connected, list all clients in a tabular format, disconnect a specific client, or shut down the server entirely.
4. **Graceful Shutdown**: When the `shutdown` command is issued, the server will disconnect all clients and close the server.

## Example Commands for the Operator

Operator: num users
Operator: list clients
Operator: disconnect <client_id>
Operator: shutdown

- **View number of connected clients**:

Operator: clients -n

- **View connected clients**:

Operator: clients -l

Output example:

Client ID                             IP            Port

8f8e8e47-abc1-4524-bf7e-474f6ad13218   127.0.0.1     56789

- **Disconnect a client**:

Operator: disconnect 8f8e8e47-abc1-4524-bf7e-474f6ad13218

- **Shutdown the server**:

Operator: shutdown

## Requirements
- Python 3.x
- External library:
- `tabulate` (for displaying tables)
  - Install via `pip install tabulate`

## Running the Server
1. Start the server:
 ```bash
 python3 server.py