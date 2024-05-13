import os
import requests
import glob
import datetime
import configparser
import sqlite3
import shutil
from cryptography.fernet import Fernet


class ConfUtils:
    DB_FILENAME = 'minipassword.db'

    def __init__(self):
        self.data_path = f'{os.path.expanduser("~")}/.minipassword'
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        self.config = configparser.ConfigParser()
        self.config_file = f'{self.data_path}/config.ini'
        self.database_file = f'{self.data_path}/{self.DB_FILENAME}'

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                self.config.write(f)

            self.config.add_section('common')
            self.config.add_section('db')

        self.config.read(self.config_file)

    def get(self, section: str, key: str):
        return self.config.get(section, key)

    def set(self, section: str, key: str, value: str):
        self.config.set(section, key, value)
        with open(self.config_file, 'w') as f:
            self.config.write(f)

        self.config.read(self.config_file)

    def create_database_file(self, database_path=None):
        if database_path is not None:
            self.database_file = f'{database_path}/{self.DB_FILENAME}'

        self.set('db', 'database_file', self.database_file)
        conn = sqlite3.connect(self.database_file)

        # Create table
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL UNIQUE,
                login_name TEXT NOT NULL,
                password TEXT NOT NULL,
                memo TEXT NULL,
                url VARCHAR(255) NULL
            )
        ''')

        conn.close()

        self.config.read(self.config_file)


class PasswordManager:

    def __init__(self, conf_utils=None):
        if conf_utils is None:
            self.conf_utils = ConfUtils()
        else:
            self.conf_utils = conf_utils

        self.database_file = self.conf_utils.get('db', 'database_file')
        self.aes_key = self.conf_utils.get('common', 'aes_key')

    def add_password(self, name, login_name, password, memo=None, url=None):
        conn = sqlite3.connect(self.database_file)
        password = self.aes_encrypt(password)
        login_name = self.aes_encrypt(login_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO passwords (name, login_name, password, memo, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, login_name, password, memo, url))
        conn.commit()
        conn.close()

    def get_password(self, query_string):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM passwords WHERE name LIKE ? OR url LIKE ? OR MEMO LIKE ?
        ''', (f'%{query_string}%', f'%{query_string}%', f'%{query_string}%'))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_password_by_id(self, password_id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM passwords WHERE id=?
        ''', (password_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_password_by_name(self, name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM passwords WHERE name=?
        ''', (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_passwords(self):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM passwords
        ''')
        result = cursor.fetchall()
        conn.close()
        return result

    def update_password(self, password_id, name, login_name, password, memo=None, url=None):
        login_name = self.aes_encrypt(login_name)
        password = self.aes_encrypt(password)
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE passwords
            SET name=?, login_name=?, password=?, memo=?, url=?
            WHERE id=?
        ''', (name, login_name, password, memo, url, password_id))
        conn.commit()
        conn.close()

    def delete_password(self, password_id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM passwords WHERE id=?
        ''', (password_id,))
        conn.commit()
        conn.close()

    def backup_db(self, backup_file=None):
        if backup_file is None:
            now = datetime.datetime.now()
            date_str = now.strftime('%Y%m%d%H%M%S')
            name, extension = os.path.splitext(self.database_file)
            backup_file = f'{name}_bak_{date_str}{extension}'

        shutil.copyfile(self.database_file, backup_file)

        return backup_file

    def upload_db(self):
        self.conf_utils.config.read(self.conf_utils.config_file)

        url = self.conf_utils.get('common', 'cloud_api')
        token = self.conf_utils.get('common', 'cloud_token')
        with open(self.database_file, 'rb') as file:
            headers = {
                'Content-Type': 'application/octet-stream',
                'Authorization': f'Bearer {token}'
            }

            response = requests.post(url, headers=headers, data=file)

            return response

    def restore_db(self):
        url = self.conf_utils.get('common', 'cloud_api')
        token = self.conf_utils.get('common', 'cloud_token')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        # need to check the content of the response if it is a valid database file?
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            # before writing the file, need to check if the response content is a valid database file
            with open(self.database_file, 'wb') as file:
                file.write(response.content)
        return response

    def destroy_db(self):
        if os.path.exists(self.database_file):
            os.remove(self.database_file)
        files = glob.glob(f'{self.conf_utils.data_path}/*')
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
        if os.path.exists(self.conf_utils.config_file):
            os.remove(self.conf_utils.config_file)

    def aes_encrypt(self, data):
        f = Fernet(self.aes_key.encode())
        return f.encrypt(data.encode()).decode()

    def aes_decrypt(self, encrypt_data):
        f = Fernet(self.aes_key.encode())
        return f.decrypt(encrypt_data.encode()).decode()





