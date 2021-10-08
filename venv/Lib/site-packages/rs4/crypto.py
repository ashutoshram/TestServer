from Crypto import Random
from Crypto.Cipher import AES as AESCipher
import base64
from hashlib import md5

def trans (key):
    return md5 (key.encode ()).hexdigest ()

class AES:
    BLCOK_SIZE = 16

    @classmethod
    def encrypt (cls, message, passphrase):
        passphrase = trans (passphrase)
        IV = Random.new ().read (cls.BLCOK_SIZE)
        aes = AESCipher.new (passphrase, AESCipher.MODE_CFB, IV)
        return base64.b64encode (IV + aes.encrypt (message))

    @classmethod
    def decrypt (cls, encrypted, passphrase):
        passphrase = trans (passphrase)
        encrypted = base64.b64decode (encrypted)
        IV = encrypted [:cls.BLCOK_SIZE]
        aes = AESCipher.new (passphrase, AESCipher.MODE_CFB, IV)
        return aes.decrypt (encrypted [cls.BLCOK_SIZE:])