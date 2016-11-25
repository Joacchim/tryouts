FD Passing
===

# Compiling

## server.c

```sh
gcc -o srv -std=c99 server.c
```

## forward.c

```sh
gcc -o fwd forward.c
```

# Using

## srv

This is the server-side, accepting clients that will give it the ownership of a
fd, and will then read everything it can from the fd retrieved, before closing
it and waiting for the next client connection.

Launch it with the following command:
```sh
./srv
```

Note that it creates a file /tmp/socketpassing.sock as the unix socket for
communication channel.

## fwd

This is the client-side of this poc. It connects to the server's unix socket,
and sends an fd on an opened file to the server for it to read and display the
data.

You can launch it with the following command:
```sh
./fwd $PATH_TO_FILE_FOR_READING
```
