import hashlib
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

padder = padding.PKCS7(128).padder()
unpadder = padding.PKCS7(128).unpadder()

def password_to_key(password: str) -> bytes:
    salt = hashlib.sha256(password.encode()).digest()[:16]
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations=100000, dklen=32)

def encrypt_into_file(password: str, input_file_path: str):
    if not os.path.exists(input_file_path) or not os.path.isfile(input_file_path):
        raise Exception("File doesn't exist")

    if os.path.splitext(input_file_path)[-1] == ".bin":
        raise Exception(f"{input_file_path} is .bin. Already encrypted")

    with open(input_file_path, "rb") as f:
        file_contents = f.read()

    key_bytes = password_to_key(password)
    cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_contents) + padder.finalize()
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    output_file_path = input_file_path + ".bin"

    with open(output_file_path, "wb") as f:
        f.write(ciphertext)


def decrypt_into_file(key_str: str, input_file_path: str):
    original_data = decrypt(key_str, input_file_path)

    output_file_path = input_file_path.removesuffix(".bin")
    with open(output_file_path, "wb") as f:
        f.write(original_data)

def decrypt(password: str, input_file_path: str):
    if not os.path.exists(input_file_path) or not os.path.isfile(input_file_path):
        raise Exception("File doesn't exist")

    if os.path.splitext(input_file_path)[-1] != ".bin":
        raise Exception(f"{input_file_path} is not .bin. Not encrypted")

    key_bytes = password_to_key(password)

    with open(input_file_path, "rb") as f:
        file_contents = f.read()

    cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(file_contents) + decryptor.finalize()

    original_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return original_data

if __name__ == "__main__":
    import argparse
    from getpass import getpass

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", action='store_true', help="Зашифрровать файл")
    group.add_argument("-d", "--decrypt", action='store_true', help="Расшифровать файл")

    parser.add_argument("-f", "--file", type=str, help="Путь к файлу", required=True)
    args = parser.parse_args()

    password = getpass("Enter password:")

    if args.encrypt:
        encrypt_into_file(password, args.file)

    elif args.decrypt:
        decrypt_into_file(password, args.file)