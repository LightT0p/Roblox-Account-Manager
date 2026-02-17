import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoEngine:
    ITERATIONS = 200000

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 32-byte key from password and salt using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=CryptoEngine.ITERATIONS,
        )
        # Return as base64 encoded key for storage
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        """Encrypts data using AES-GCM"""
        try:
            # Decode the base64 key back to bytes
            key_bytes = base64.urlsafe_b64decode(key)
            aesgcm = AESGCM(key_bytes)
            
            # Generate a random 12-byte nonce
            nonce = os.urandom(12)
            
            # Encrypt the data
            ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
            
            # Combine nonce and ciphertext and encode as base64
            return base64.b64encode(nonce + ciphertext).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {e}")
            return None

    @staticmethod
    def decrypt(encrypted_data: str, key: bytes) -> str:
        """Decrypts data using AES-GCM"""
        try:
            # Decode the base64 key back to bytes
            key_bytes = base64.urlsafe_b64decode(key)
            
            # Decode the encrypted data
            raw_data = base64.b64decode(encrypted_data)
            
            # Extract nonce (first 12 bytes) and ciphertext
            nonce = raw_data[:12]
            ciphertext = raw_data[12:]
            
            # Decrypt
            aesgcm = AESGCM(key_bytes)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a random salt for key derivation"""
        return os.urandom(16)