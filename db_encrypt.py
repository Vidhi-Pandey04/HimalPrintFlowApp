# db_encrypt.py — run this to encrypt your database backup
# pip install cryptography

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64, os

def get_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_db(password: str):
    salt = os.urandom(16)
    key = get_key(password, salt)
    f = Fernet(key)
    with open('himal.db', 'rb') as file:
        encrypted = f.encrypt(file.read())
    with open('himal.db.enc', 'wb') as file:
        file.write(salt + encrypted)
    print('Encrypted → himal.db.enc')

def decrypt_db(password: str):
    with open('himal.db.enc', 'rb') as file:
        data = file.read()
    salt = data[:16]
    key = get_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(data[16:])
    with open('himal.db.restored', 'wb') as file:
        file.write(decrypted)
    print('Decrypted → himal.db.restored')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: python db_encrypt.py encrypt|decrypt yourpassword')
        sys.exit(1)
    action, password = sys.argv[1], sys.argv[2]
    if action == 'encrypt':
        encrypt_db(password)
    elif action == 'decrypt':
        decrypt_db(password)