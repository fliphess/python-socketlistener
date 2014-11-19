from SimpleAES import SimpleAES, DecryptionError, EncryptionError


class CryptoException(Exception):
    pass


class Crypto(object):
    def __init__(self, psk):
        self.aes = SimpleAES(psk)

    def decrypt(self, string):
        try:
            return self.aes.decrypt(string)
        except DecryptionError as e:
            raise CryptoException(e)

    def encrypt(self, string):
        try:
            return self.aes.encrypt(string)
        except EncryptionError as e:
            raise CryptoException(e)
