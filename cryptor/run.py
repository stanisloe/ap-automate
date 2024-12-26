import argparse
from getpass import getpass

from cryptor.crypt_manager import encrypt_into_file, decrypt_into_file

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-e", "--encrypt", action='store_true', help="Зашифрровать файл")
group.add_argument("-d", "--decrypt", action='store_true', help="Расшифровать файл")

parser.add_argument("-f", "--file", type=str, help="Путь к файлу", required=True)
args = parser.parse_args()

key = getpass("Enter encryption key:")

if args.encrypt:
    encrypt_into_file(key, args.file)

elif args.decrypt:
    decrypt_into_file(key, args.file)