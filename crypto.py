# crypto.py

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def generate_salt(size: int) -> bytes:
    return os.urandom(size)


def derive_key(password: str, salt: bytes, iterations: int, length: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_field(plaintext: str, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce (recommended)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext  # store together


def decrypt_field(ciphertext: bytes, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    encrypted = ciphertext[12:]
    plaintext = aesgcm.decrypt(nonce, encrypted, None)
    return plaintext.decode()
