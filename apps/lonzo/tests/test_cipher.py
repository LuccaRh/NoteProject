# Imports
from lonzo.core.cipher import decrypt, encrypt


# Code
# What goes in comes back, and the token does not show it
def test_encrypt_hides_the_text_and_decrypt_brings_it_back() -> None:

    token = encrypt(text="sk-ant-secret")

    assert b"sk-ant-secret" not in token
    assert decrypt(token=token) == "sk-ant-secret"
