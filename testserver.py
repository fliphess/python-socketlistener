#!/usr/bin/env python
import time
from python_socketlistener.client import SocketSender
from python_socketlistener.server import queue, SocketServerCtl

users = {'flip': 'plop'}
host = '127.0.0.1'
port = 6666
verbose = True
data = "efkjrwgmnsrkjdfxvreangklstbjknxd"

print "@" * 20
print "Starting loop"
print "@" * 20
server = SocketServerCtl(users=users, host=host, port=port, verbose=verbose)
server.start()
print "Server started"

print "@" * 20
print "Sending command %s" % data
print "@" * 20
client = SocketSender(user='flip', psk='plop', host=host, port=port)
client.send(data)
client.close()
time.sleep(0.1)
print "Done"

print "@" * 20
print "Stopping server"
print "@" * 20
server.stop()

print "@" * 20
print queue
print "@" * 20
