import asyncore
from base64 import b64decode
import socket
import threading
import time
from python_socketlistener.crypto import Crypto, CryptoException
from python_socketlistener.queue import SocketEvent, queue


class SocketListenerError(Exception):
    pass


class SocketListener(asyncore.dispatcher):
    def __init__(self, users, host='127.0.0.1', port=6666, verbose=True):
        self.users = users
        self.host = host
        self.port = port
        self.verbose = verbose

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.host, self.port))
        self.listen(5)

    def handle_accept(self):
        connection, address = self.accept()
        if self.verbose:
            self.log("[Connection] incoming tcp connection from %s:%s" % address)
        TcpDispatcher(connection, address, self.users, self.verbose)


class TcpDispatcher(asyncore.dispatcher_with_send):
    def __init__(self, connection, address, users, verbose):
        asyncore.dispatcher.__init__(self, connection)
        self.connection = connection
        self.address = address
        self.users = users
        self.verbose = verbose

        self.from_remote_buffer = ''
        self.to_remote_buffer = ''
        self.sender = None

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()
        if self.verbose:
            self.log("[Close] Closed connection from %s:%s" % self.address)

    def writable(self):
        return len(self.to_remote_buffer) > 0

    def handle_write(self):
        sent = self.send(self.to_remote_buffer)
        self.to_remote_buffer = self.to_remote_buffer[sent:]

    def handle_read(self):
        user = 'unknown'
        data = self.recv(4096)
        if not data:
            self.close()
            return
        self.from_remote_buffer += data

        try:
            user, string = b64decode(data).split(':')
            psk = self._get_psk(user=user)

            if not psk:
                if self.verbose:
                    self.log("[%s] - No psk found for user %s" % (self.address[0], user))
                return False

            decrypted_data = Crypto(psk=psk).decrypt(string=string)
            if not decrypted_data:
                raise CryptoException('Failed to decrypt incoming data')

            if self.verbose:
                self.log('[Incoming] - %s - %s - %s' % (user, self.address, decrypted_data))
            queue.add(SocketEvent(data=decrypted_data, address=self.address, user=user, time=time.ctime()))
        except (ValueError, TypeError) as e:
            if self.verbose:
                self.log('Failed to decode data from %s: %s' % (str(self.address), e))
            return False

        except CryptoException as e:
            if self.verbose:
                self.log("[Decryption] Failed to decrypt input for user %s - %s: %s" % (self.address, user, e))
            return False

    def _get_psk(self, user):
        if user in self.users:
            return self.users[user]
        return False


class SocketListenerCtl(threading.Thread):
    def __init__(self, users, host, port, verbose=True):
        super(SocketListenerCtl, self).__init__()
        self.server = None
        self.host = host
        self.port = port
        self.users = users
        self.verbose = verbose
        self.continue_running = True

    def run(self):
        self.server = SocketListener(host=self.host, port=self.port, users=self.users, verbose=self.verbose)
        while self.continue_running:
            asyncore.poll()

    def stop(self):
        self.continue_running = False

    def running(self):
        return self.continue_running

    def reload(self):
        self.continue_running = False
        self.start()
