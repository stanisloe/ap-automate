import argparse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

padder = padding.PKCS7(128).padder()
unpadder = padding.PKCS7(128).unpadder()

def encrypt_into_file(key: bytes, input_file_path: str):

    if not key.__len__() == 32:
        raise Exception("Key must be 32 bytes(256 bits)")
    if os.path.splitext(input_file_path)[-1] == ".bin":
        raise Exception(f"{input_file_path} is .bin. Already encrypted")

    if not os.path.exists(input_file_path) or not os.path.isfile(input_file_path):
        raise Exception("File doesn't exist")

    with open(input_file_path, "rb") as f:
        file_contents = f.read()

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_contents) + padder.finalize()
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    output_file_path = input_file_path + ".bin"

    with open(output_file_path, "wb") as f:
        f.write(ciphertext)


def decrypt_into_file(key: bytes, input_file_path: str, ):
    original_data = decrypt(key, input_file_path)

    output_file_path = input_file_path.removesuffix(".bin")
    with open(output_file_path, "wb") as f:
        f.write(original_data)

def decrypt(key: bytes, input_file_path: str):
    if os.path.splitext(input_file_path)[-1] != ".bin":
        raise Exception(f"{input_file_path} is not .bin. Not encrypted")

    if not os.path.exists(input_file_path) or not os.path.isfile(input_file_path):
        raise Exception("File doesn't exist")

    with open(input_file_path, "rb") as f:
        file_contents = f.read()

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(file_contents) + decryptor.finalize()

    original_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return original_data


def validate_key(value):
    if len(value) != 64:
        raise Exception("AES-256 key must have 64 hexadecimal digits")
    return bytes.fromhex(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", action='store_true', help="Зашифрровать файл")
    group.add_argument("-d", "--decrypt", action='store_true', help="Расшифровать файл")

    parser.add_argument("-f", "--file", type=str, help="Путь к файлу", required=True)
    parser.add_argument("-k", "--key", type=validate_key, help="Ключ шифрования", required=True)
    args = parser.parse_args()

    if args.encrypt:
        encrypt_into_file(args.key, args.file)

    elif args.decrypt:
        decrypt_into_file(args.key, args.file)
