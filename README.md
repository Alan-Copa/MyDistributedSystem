# MyDistributedSystem

This repository contains solutions for three coding assignments in a Distributed Systems course (Autumn 2024/25). The assignments focus on building a multi-threaded chat server, implementing structured messaging with Protocol Buffers, and transitioning from a client-server architecture to a peer-to-peer communication model.


### Developer Tips

Compile .proto files

```
protoc --python_out=. template.proto
```

Avoid "address already in use" error

```
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```