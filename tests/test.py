import logging
import socket
import mock
from unittest2 import TestCase


class SocketTestCase(TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        super(SocketTestCase, self).setUp()
        logging.disable(logging.CRITICAL)

        self.host = '127.0.0.1'
        self.port = self.get_free_port()
        self.users = {"bob": "foo", "alice": "bar"}

    def get_free_port(self):
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def setup_patch(self, to_patch):
        patcher = mock.patch(to_patch)
        self.addCleanup(patcher.stop)
        return patcher.start()



