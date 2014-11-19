import socket
import time
from python_socketserver.client import SocketSender
from python_socketserver.server import SocketInputQueue, SocketEvent, SocketServerCtl, SocketServer
from tests.test import SocketTestCase


class TestSocketEvent(SocketTestCase):
    def test_that_socket_event_returns_a_dict(self):
        s = SocketEvent(a=1, b=2, c=3)
        self.assertEqual(s, {'a': 1, 'c': 3, 'b': 2})

    def test_that_socket_event_does_not_return_additional_vars(self):
        s = SocketEvent(a=1, b=2, c=3)
        self.assertEqual(vars(s), {})

    def test_that_socket_event_returns_an_empty_dict_when_no_args(self):
        s = SocketEvent()
        self.assertEqual(s, {})
        self.assertEqual(vars(s), {})


class TestSocketInputQueue(SocketTestCase):
    def tearDown(self):
        SocketInputQueue._instance = None
        super(TestSocketInputQueue, self).tearDown()

    def test_that_socket_queue_always_returns_the_same_instance(self):
        b = SocketInputQueue()
        c = SocketInputQueue()
        self.assertTrue(b == c)

    def test_that_socket_queue_returns_a_list(self):
        a = SocketInputQueue()
        self.assertEqual(a, [])
        self.assertIsInstance(a, list)

    def test_that_add_appends_input_to_list(self):
        a = SocketInputQueue()
        a.add('foo')
        self.assertEqual(a, ['foo'])
        a.add('bar')
        self.assertEqual(a, ['foo', 'bar'])

    def test_that_flush_clears_out_the_queue(self):
        a = SocketInputQueue()
        a.add('foo')
        self.assertEqual(a, ['foo'])
        a.flush()
        self.assertEqual(a, [])

    def test_that_get_pops_first_element_from_list(self):
        a = SocketInputQueue()
        a.add('foo')
        a.add('bar')
        a.add(1337)
        self.assertEqual(a, ['foo', 'bar', 1337])
        b = a.get()
        self.assertEqual(a, ['bar', 1337])
        self.assertEqual(b, 'foo')
        c = a.get()
        self.assertEqual(a, [1337])
        self.assertEqual(c, 'bar')
        d = a.get()
        self.assertEqual(a, [])
        self.assertEqual(d, 1337)
        self.assertFalse(a.get())

    def test_that_get_returns_false_when_list_is_empty(self):
        a = SocketInputQueue()
        self.assertFalse(a.get())


class TestSocketServerGetPsk(SocketTestCase):
    def tearDown(self):
        super(TestSocketServerGetPsk, self).tearDown()
        self.server.close()

    def setUp(self):
        super(TestSocketServerGetPsk, self).setUp()
        self.server = SocketServer(port=self.port, users=self.users)

    def test_that_get_psk_returns_psk_when_user_is_present(self):
        self.assertEqual(self.server._get_psk(user='bob'), 'foo')
        self.assertEqual(self.server._get_psk(user='alice'), 'bar')

    def test_that_get_psk_returns_false_when_no_psk_present_for_user(self):
        self.assertFalse(self.server._get_psk(user='craig'))
        self.assertFalse(self.server._get_psk(user='eve'))


class TestSocketServer(SocketTestCase):
    def setUp(self):
        super(TestSocketServer, self).setUp()
        self.server = SocketServerCtl(host=self.host, port=self.port, users=self.users, verbose=False)
        self.client = SocketSender(user='bob', psk='foo', host='127.0.0.1', port=self.port)
        self.server.start()

    def tearDown(self):
        super(TestSocketServer, self).tearDown()
        self.server.stop()
        self.client.close()
        from python_socketserver.server import queue
        queue.flush()

    def test_that_socket_server_adds_event_to_queue_when_data_can_be_decrypted(self):
        self.client.send('test event')
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue[0]['address'][0], '127.0.0.1')
        self.assertEqual(queue[0]['data'], 'test event')
        self.assertEqual(queue[0]['user'], 'bob')

    def test_that_not_only_the_first_user_can_send(self):
        c = SocketSender(user='alice', psk='bar', host='127.0.0.1', port=self.port)
        c.send('alice sends')
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue[0]['address'][0], '127.0.0.1')
        self.assertEqual(queue[0]['data'], 'alice sends')
        self.assertEqual(queue[0]['user'], 'alice')

    def test_that_socket_server_events_are_different_events_in_queue(self):
        c = SocketSender(user='alice', psk='bar', host='127.0.0.1', port=self.port)
        c.send('alice sends')
        c.close()
        time.sleep(0.1)
        self.client.send('bob sends')
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue[0]['user'], 'alice')
        self.assertEqual(queue[0]['data'], 'alice sends')
        self.assertEqual(queue[1]['user'], 'bob')
        self.assertEqual(queue[1]['data'], 'bob sends')

    def test_that_socket_server_does_not_add_event_to_queue_when_data_can_not_be_decrypted(self):
        c = SocketSender(user='alice', psk='fooo', host='127.0.0.1', port=self.port)
        c.send('alice sends')
        c.close()
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue, [])

    def test_that_socket_server_does_not_add_event_to_queue_when_user_not_found(self):
        a = SocketSender(user='flip', psk='fooo', host='127.0.0.1', port=self.port)
        a.send('alice sends')
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue, [])

    def test_that_socket_server_does_not_add_event_to_queue_when_data_is_bogus(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto('bogus data', (self.host, self.port))
        s.close()
        time.sleep(0.1)

        from python_socketserver.server import queue
        self.assertEqual(queue, [])
