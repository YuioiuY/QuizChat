import os 
import json

class Crypt():
    def __init__(self):
        self.file_path = 'source/source.json'
        
    def token_Factory(self):
        token = ''
        if self.file_path .endswith('.json'): 
            with open(self.file_path , 'r', encoding='utf-8') as f:
                try:
                    token = json.load(f)  
                except json.JSONDecodeError as e:
                    print(f"Ошибка чтения файла {self.file_path}: {e}")

        return self.decrypt_from_hex(token['token'])

    def encrypt_to_hex(self, input_string):
        return ''.join(format(ord(char), '02x') for char in input_string)


    def decrypt_from_hex(self, hex_string):
        if not isinstance(hex_string, str):
            raise ValueError(f"Expected a string, but got {type(hex_string)}")
        return ''.join(chr(int(hex_string[i:i+2], 16)) for i in range(0, len(hex_string), 2))


