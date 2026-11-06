# Imports
import os

from cryptography.fernet import Fernet


# Global variables
fernet = Fernet(os.environ["LONZO_SECRET_KEY"])


# Code
def encrypt(text: str) -> bytes:
    """
    The text encrypted with the secret of the service
    """

    return fernet.encrypt(text.encode())


def decrypt(token: bytes) -> str:
    """
    The text back from what encrypt made
    """

    return fernet.decrypt(token).decode()
