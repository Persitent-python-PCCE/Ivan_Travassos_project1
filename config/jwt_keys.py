
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE_DIR = Path(__file__).resolve().parent.parent
KEY_DIR = BASE_DIR / "keys"
PRIVATE_KEY_FILE = KEY_DIR / "private.pem"
PUBLIC_KEY_FILE = KEY_DIR / "public.pem"


def ensure_keys():
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    if not PRIVATE_KEY_FILE.exists() or not PUBLIC_KEY_FILE.exists():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        PRIVATE_KEY_FILE.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        PUBLIC_KEY_FILE.write_bytes(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


def load_keys():
    ensure_keys()
    return PRIVATE_KEY_FILE.read_text(), PUBLIC_KEY_FILE.read_text()
