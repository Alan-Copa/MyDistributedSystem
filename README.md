# MyDistributedSystem


### Developer Tips

Compile .proto files

```
protoc --python_out=. template.proto
```

Avoid "address already in use" error

```
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```