python-socketlistener
=====================

A very basic client server setup for sending data encrypted over a unix or tcp socket.


# Install 
``` pip install python-socketlistener ```

## Run Server
```python

    from python_socketserver.server import SocketServerCtl

    server = SocketServerCtl(users={"flip": "plop"}, 
                            host='127.0.0.1', 
                            port=6666, 
                            verbose=True)
    server.start()
```

## Stop Server
```python

    server.stop
```

You can check the status of the server with ```server.running()```

## Process results

```python

    from python_socketserver.server import queue 

    task = queue.get()
    if task:
        ...
        do_something_to_process(task)
        ...
```       

To clear the queue run ```queue.flush()```


## Send to server
```python

    from python_socketserver.client import SocketSender
    a = SocketSender(user='flip', psk='plop')
    a.send('Some string to be send')
    a.close()

```

Or with the added script:

```sh

export SOCKET_USER='flip'
export SOCKET_PSK='plop'

bin/send2socket -s 127.0.0.1 -p 6666 -d plop

```

## TODO 
[X] - Replace simple AES with another one that does not have an ugly stderr msg, which is in the debian repo
[ ] - Write tests for client
[ ] - Make tcp and unix socket possible
