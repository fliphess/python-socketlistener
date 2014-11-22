import socket
import time
from python_socketlistener.client import SocketSender
from python_socketlistener.queue import queue
from python_socketlistener.server import SocketListenerCtl, TcpDispatcher
from tests.test import SocketTestCase


class TestTcpDispatcherGetPsk(SocketTestCase):

    def setUp(self):
        super(TestTcpDispatcherGetPsk, self).setUp()
        self.server = TcpDispatcher(connection=None, users=self.users, address=None, verbose=False)

    def test_that_get_psk_returns_psk_when_user_is_present(self):
        self.assertEqual(self.server._get_psk(user='bob'), 'foo')
        self.assertEqual(self.server._get_psk(user='alice'), 'bar')

    def test_that_get_psk_returns_false_when_no_psk_present_for_user(self):
        self.assertFalse(self.server._get_psk(user='craig'))
        self.assertFalse(self.server._get_psk(user='eve'))


class TestSocketServer(SocketTestCase):

    def setUp(self):
        super(TestSocketServer, self).setUp()
        self.server = SocketListenerCtl(host=self.host, port=self.port, users=self.users, verbose=False)
        self.server.start()
        time.sleep(0.1)

    def tearDown(self):
        super(TestSocketServer, self).tearDown()
        self.server.stop()
        queue.flush()

    def test_that_socket_server_adds_event_to_queue_when_data_can_be_decrypted(self):
        SocketSender(user='bob', psk='foo', host='127.0.0.1', port=self.port).send('test event 1')
        time.sleep(0.1)

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]['address'][0], '127.0.0.1')
        self.assertEqual(queue[0]['data'], 'test event 1')
        self.assertEqual(queue[0]['user'], 'bob')

    def test_that_not_only_the_first_user_can_send(self):
        SocketSender(user='alice', psk='bar', host='127.0.0.1', port=self.port).send('alice sends 2')
        time.sleep(0.1)

        self.assertEqual(queue[0]['address'][0], '127.0.0.1')
        self.assertEqual(queue[0]['data'], 'alice sends 2')
        self.assertEqual(queue[0]['user'], 'alice')

    def test_that_socket_server_events_are_different_events_in_queue(self):
        SocketSender(user='alice', psk='bar', host='127.0.0.1', port=self.port).send('alice sends 3')
        SocketSender(user='bob', psk='foo', host='127.0.0.1', port=self.port).send('bob sends 4')
        time.sleep(0.1)

        self.assertEqual(len(queue), 2)
        self.assertEqual(queue[0]['user'], 'alice')
        self.assertEqual(queue[0]['data'], 'alice sends 3')

        self.assertEqual(queue[1]['user'], 'bob')
        self.assertEqual(queue[1]['data'], 'bob sends 4')

    def test_that_socket_server_does_not_add_event_to_queue_when_data_can_not_be_decrypted(self):
        SocketSender(user='alice', psk='fooo', host='127.0.0.1', port=self.port).send('alice sends 5')
        time.sleep(0.1)

        self.assertEqual(len(queue), 0)
        self.assertEqual(queue, [])

    def test_that_socket_server_does_not_add_event_to_queue_when_user_not_found(self):
        SocketSender(user='flip', psk='fooo', host='127.0.0.1', port=self.port).send('alice sends')
        time.sleep(0.1)

        self.assertEqual(len(queue), 0)
        self.assertEqual(queue, [])

    def test_that_socket_server_does_not_add_event_to_queue_when_data_is_bogus(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send('bogus data')
        s.close()
        time.sleep(0.1)
        self.assertEqual(len(queue), 0)
        self.assertEqual(queue, [])
