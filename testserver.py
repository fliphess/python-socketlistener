#!/usr/bin/env python
import time
from python_socketlistener.client import SocketSender
from python_socketlistener.server import SocketListenerCtl
from python_socketlistener.queue import queue

users = {'flip': 'plop'}
host = ''
port = 6666
verbose = True
data = "dit is een boodschap van flipje verzonden over tcp enkel om te testen of het werkt"

server = SocketListenerCtl(users=users, host=host, port=port, verbose=verbose)

try:
    print "@" * 20, "Starting loop", "@" * 20
    server.start()
    print "Server started"


    print "@" * 20, "Sending command %s" % data, "@" * 20
    client = SocketSender(user='flip', psk='plop', host=host, port=port)
    client.send(data)
    client.close()
    time.sleep(0.1)


    print "@" * 20, "QUEUE", "@" * 20
    print queue
    print "@" * 20

finally:
    server.stop()
