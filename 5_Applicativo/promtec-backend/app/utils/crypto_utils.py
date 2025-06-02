"""
Cryptography Utilities Module.

This module provides utilities for encrypting and decrypting sensitive data
using the Fernet symmetric encryption algorithm from the cryptography package.
The encryption key is loaded from environment variables for security.
"""
from cryptography.fernet import Fernet  # Symmetric encryption implementation
import base64  # For encoding and decoding binary data
import os  # For accessing environment variables
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Get the encryption key from environment variables
FERNET_KEY = os.environ.get('FERNET_KEY')
# Initialize the Fernet encryption system with the key
fernet = Fernet(FERNET_KEY)

def encrypt_value(value):
    """
    Encrypt a string value using Fernet symmetric encryption.
    
    This function takes a string value, encrypts it using the Fernet key,
    and returns the encrypted value as a base64-encoded string.
    
    Args:
        value (str): The string value to encrypt, or None
        
    Returns:
        str: The encrypted value as a base64-encoded string, or None if input was None
    """
    if value is None:
        return None
    return fernet.encrypt(value.encode()).decode()  # Encrypt and convert to string

def decrypt_value(value):
    """
    Decrypt an encrypted string value using Fernet symmetric encryption.
    
    This function takes an encrypted base64-encoded string, decrypts it 
    using the Fernet key, and returns the original plaintext string.
    
    Args:
        value (str): The encrypted string value to decrypt, or None
        
    Returns:
        str: The decrypted plaintext value, or None if input was None
        
    Raises:
        cryptography.fernet.InvalidToken: If the encrypted value is invalid or was 
                                         encrypted with a different key
    """
    if value is None:
        return None
    return fernet.decrypt(value.encode()).decode()  # Decrypt and convert to string
