from python_socketlistener.queue import SocketEvent, SocketInputQueue
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
