import asyncore
from base64 import b64decode
import socket
import threading
import time

from python_socketlistener.crypto import Crypto, CryptoException


class SocketInputQueue(list):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SocketInputQueue, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def add(self, event):
        self.append(event)

    def get(self):
        try:
            return self.pop(0)
        except IndexError:
            return False

    def flush(self):
        self[:] = []

queue = SocketInputQueue()


class SocketEvent(dict):
    def __init__(self, **kwargs):
        super(SocketEvent, self).__init__()
        self.update(kwargs)


class SocketListenerError(Exception):
    pass


class SocketServer(asyncore.dispatcher):
    def __init__(self, users, host='127.0.0.1', port=6666, verbose=True):
        self.verbose = verbose
        self.host = host
        self.port = port
        self.users = users

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))

    def handle_connect(self):
        if self.verbose:
            self.log("[Connection] %s" % vars(self))

    def handle_close(self):
        self.close()
        if self.verbose:
            self.log("[Close] Closed connection to %s" % self.host)

    def handle_read(self):
        user = 'unknown'
        data, address = self.recvfrom(2048)
        if not data:
            return

        try:
            user, string = b64decode(data).split(':')
            psk = self._get_psk(user=user)
            if not psk:
                if self.verbose:
                    self.log("[%s] - No psk found for user %s" % (address, user))
                return False
            decrypted_data = Crypto(psk=psk).decrypt(string=string)
            if self.verbose:
                self.log('[Incoming] - %s - %s - %s' % (user, address, decrypted_data))
            if decrypted_data:
                queue.add(SocketEvent(data=decrypted_data, address=address, user=user, time=time.ctime()))
            else:
                raise CryptoException('Failed to decrypt incoming data')

        except (ValueError, TypeError):
            if self.verbose:
                self.log('Failed to decode data from %s' % address)
            return False

        except CryptoException as e:
            if self.verbose:
                self.log("[Decryption] Failed to decrypt input for user %s - %s: %s" % (address, user, e))
            return False

    def _get_psk(self, user):
        if user in self.users:
            return self.users[user]
        return False


class SocketServerCtl(threading.Thread):
    def __init__(self, users, host, port, verbose):
        super(SocketServerCtl, self).__init__()
        self.server = None
        self.host = host
        self.port = port
        self.users = users
        self.verbose = verbose
        self.continue_running = True

    def run(self):
        self.server = SocketServer(host=self.host, port=self.port, users=self.users, verbose=self.verbose)
        while self.continue_running:
            asyncore.poll()

    def stop(self):
        self.continue_running = False

    def running(self):
        return self.continue_running

    def reload(self):
        self.continue_running = False
        self.start()
