from base64 import b64encode
import socket
from python_socketserver.crypto import Crypto


class SocketSenderError(Exception):
    pass


class SocketSender(object):
    """ A simple socket sender using a pre shared key to encrypt communication.
    """
    def __init__(self, user, psk, host='127.0.0.1', port=6666):
        self.psk = psk
        self.user = user
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        return self.socket.close()

    def send(self, string):
        c = Crypto(psk=self.psk)
        output = b64encode('%s:%s' % (self.user, c.encrypt(string=string)))
        try:
            self.socket.sendto(output, (self.host, self.port))
        except socket.error as e:
            raise SocketSenderError('Failed to send to %s:%s: %s' % (self.host, self.port, e))
        return True
