from cryptography.fernet import Fernet

from app.config import settings


def get_fernet() -> Fernet:
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY is not set. Generate one with: Fernet.generate_key()")
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> bytes:
    f = get_fernet()
    return f.encrypt(value.encode())


def decrypt_value(encrypted: bytes) -> str:
    f = get_fernet()
    return f.decrypt(encrypted).decode()
