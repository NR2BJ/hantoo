from cryptography.fernet import Fernet

from app.services.settings_service import app_settings


def get_fernet() -> Fernet:
    key = app_settings.get("encryption_key")
    if not key:
        raise ValueError("Encryption key not initialized. Complete setup first.")
    return Fernet(key.encode())


def encrypt_value(value: str) -> bytes:
    return get_fernet().encrypt(value.encode())


def decrypt_value(encrypted: bytes) -> str:
    return get_fernet().decrypt(encrypted).decode()
