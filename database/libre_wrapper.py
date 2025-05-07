import os
import tempfile
from typing import Tuple, Optional
from database.enums import TipAlgoritm, TipCheie
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.backends import default_backend
import base64

class LibreWrapper:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="libre_wrapper_")
        self.backend = default_backend()
    
    def __del__(self):
        # Cleanup temporary directory
        try:
            os.rmdir(self.temp_dir)
        except:
            pass

    def generate_key(self, algorithm: str, key_name: str) -> Tuple[bytes, bytes]:
        """
        Generate encryption keys using cryptography library
        Returns tuple of (private_key, public_key) for RSA, or (key, None) for AES
        """
        if algorithm == "AES-Libre":
            # Generate AES key (32 bytes = 256 bits)
            key = os.urandom(32)
            return key, None
            
        elif algorithm == "RSA-Libre":
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.backend
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return private_pem, public_pem
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def encrypt(self, algorithm: str, input_file: str, output_file: str, key: bytes, 
                key_type: Optional[TipCheie] = None) -> None:
        """
        Encrypt a file using cryptography library
        """
        if algorithm == "AES-Libre":
            # Read input file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # Generate IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Pad data
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Encrypt
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Write output (IV + encrypted data)
            with open(output_file, 'wb') as f:
                f.write(iv)
                f.write(encrypted_data)
                
        elif algorithm == "RSA-Libre":
            if key_type != TipCheie.PUBLICA:
                raise ValueError("RSA encryption requires a public key")
            
            # Read input file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # Load public key
            public_key = serialization.load_pem_public_key(
                key,
                backend=self.backend
            )
            
            # Encrypt
            encrypted_data = public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=asym_padding.SHA256()),
                    algorithm=asym_padding.SHA256(),
                    label=None
                )
            )
            
            # Write output
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def decrypt(self, algorithm: str, input_file: str, output_file: str, key: bytes,
                key_type: Optional[TipCheie] = None) -> None:
        """
        Decrypt a file using cryptography library
        """
        if algorithm == "AES-Libre":
            # Read input file
            with open(input_file, 'rb') as f:
                iv = f.read(16)  # Read IV
                encrypted_data = f.read()  # Read encrypted data
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            # Write output
            with open(output_file, 'wb') as f:
                f.write(data)
                
        elif algorithm == "RSA-Libre":
            if key_type != TipCheie.PRIVATA:
                raise ValueError("RSA decryption requires a private key")
            
            # Read input file
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                key,
                password=None,
                backend=self.backend
            )
            
            # Decrypt
            data = private_key.decrypt(
                encrypted_data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=asym_padding.SHA256()),
                    algorithm=asym_padding.SHA256(),
                    label=None
                )
            )
            
            # Write output
            with open(output_file, 'wb') as f:
                f.write(data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}") 