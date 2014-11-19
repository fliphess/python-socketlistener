from python_socketlistener.crypto import Crypto, CryptoException
from tests.test import SocketTestCase


class TestAuthEncryptDecrypt(SocketTestCase):

    def setUp(self):
        self.psk = 'somepresharedkey'
        self.string = 'This is a string 245352467368$ikruy"REA~FV!@#$%^'

    def test_that_an_encrypted_string_can_be_decrypted(self):
        encrypted_value = Crypto(psk=self.psk).encrypt(self.string)
        decrypted_value = Crypto(psk=self.psk).decrypt(encrypted_value)
        self.assertEqual(decrypted_value, self.string)

    def test_that_decryption_raises_an_exception_when_incoming_data_cannot_be_decrypted(self):
        encrypted_value = Crypto(psk=self.psk).encrypt(self.string)
        bogus_data = encrypted_value[:-1] + 'x'
        with self.assertRaises(CryptoException):
            Crypto(psk=self.psk).decrypt(bogus_data)
