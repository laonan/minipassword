import configparser
import os
import re
import argparse
from simple_term_menu import TerminalMenu
from cryptography.fernet import Fernet
from .box import ConfUtils, PasswordManager


parser = argparse.ArgumentParser(description='Mini Password is a command-line password manager.')
parser.add_argument('-a', '--add', action='store_true', help='add a new password')
parser.add_argument('-d', '--delete', action='store_true', help='delete a password')
parser.add_argument('-u', '--update', action='store_true', help='update a password')
parser.add_argument('-l', '--list-file', action='store_true', help='list database file and configuration file paths')
parser.add_argument('-b', '--backup', action='store_true', help='backup the database file')
parser.add_argument('-p', '--upload', action='store_true', help='upload the database file to a cloud service')
parser.add_argument('-r', '--restore', action='store_true', help='restore the database file from cloud service')
parser.add_argument('-api', '--api', action='store_true', help='set cloud API url and token')
parser.add_argument('-dd', '--destroy', action='store_true', help='destroy the database, all data will be lost!')
args = parser.parse_args()


class CommandHandler:

    def __init__(self):
        self.conf_utils = ConfUtils()
        self.run_trigger = True
        self.add_arg = args.add
        self.delete_arg = args.delete
        self.update_arg = args.update
        self.list_files_arg = args.list_file
        self.destroy_arg = args.destroy
        self.backup_arg = args.backup
        self.upload_arg = args.upload
        self.restore_arg = args.restore
        self.api_arg = args.api

        try:
            self.conf_utils.get('db', 'database_file')
            self.conf_utils.get('common', 'aes_key')
        except (configparser.NoSectionError, configparser.NoOptionError):

            self.run_trigger = False
            try:
                res = input(f'Enter the database file path ({self.conf_utils.data_path}/{self.conf_utils.DB_FILENAME}): ')
                if res == '':
                    self.conf_utils.create_database_file()
                else:
                    self.conf_utils.create_database_file(res)

                df = self.conf_utils.get('db', 'database_file')
                print(f'Database file created: {df}')

                aes_key = Fernet.generate_key()
                aes_key_string = aes_key.decode('utf-8')
                self.conf_utils.set('common', 'aes_key', aes_key_string)
                print(f'AES key is generated, please keep it in a safe place: {aes_key_string}')

                self.conf_utils.config.read(self.conf_utils.config_file)
            except KeyboardInterrupt:
                print('Interrupted by user!')
                return

        self.password_manager = PasswordManager(conf_utils=self.conf_utils)

    def run(self):

        if self.add_arg:
            self.add_password()
            return

        if self.delete_arg:
            self.delete_password()
            return

        if self.update_arg:
            self.update_password()
            return

        if self.list_files_arg:
            self.list_files()
            return

        if self.backup_arg:
            self.backup_db()
            return

        if self.upload_arg:
            self.upload()
            return

        if self.restore_arg:
            self.restore()
            return

        if self.api_arg:
            self.set_api_token()
            return

        if self.destroy_arg:
            confirm = input('Are you sure you want to destroy the database file? If you have backups, ensure that you also have the secret key to restore (Y/n):')
            if confirm == 'Y':
                self.password_manager.destroy_db()
                print('Database destroyed!')
            return

        if not self.run_trigger:
            return

        os.system('clear')
        try:
            query_string = input('Enter a query string: ')
            passwords = self.password_manager.get_password(query_string)
            if len(passwords) > 0:
                if len(passwords) == 1:
                    self.show_password(passwords[0])
                else:
                    menu_items = [f'#{password[0]} \| name: {password[1]} \| url: {password[5]} \| {password[4]}' for password in passwords]
                    menu = TerminalMenu(menu_items)
                    menu_entry_index = menu.show()
                    selected_password = passwords[menu_entry_index]
                    self.show_password(selected_password)
            else:
                print('No password found!')

        except KeyboardInterrupt:
            print('Interrupted by user!')
            return

    def add_password(self):
        try:
            os.system('clear')
            name = input('Enter the name: ')

            if name == '':
                print('Name is required!')
                return

            password_obj = self.password_manager.get_password_by_name(name)
            if password_obj:
                print(f'Password already exists! (name is {name})')
                return

            login_name = input('Enter the login name: ')
            if login_name == '':
                print('Login name is required!')
                return

            password = input('Enter the password: ')
            if password == '':
                print('Password is required!')
                return

            memo = input('Enter the memo: ')
            url = input('Enter the url: ')
            if url != '' and not self.is_valid_url(url):
                while True:
                    url = input('Invalid url! Please enter a valid url or leave it blank: ')
                    if self.is_valid_url(url) or url == '':
                        break

            self.password_manager.add_password(name, login_name, password, memo, url)
            print('Password added!')
        except KeyboardInterrupt:
            print('Interrupted by user!')
            return

    def delete_password(self):
        try:
            password_id = input('Enter password id: ')
            confirm = input(f'Are you sure you want to delete password id {password_id}? (y/n): ')
            if confirm.lower() != 'y':
                return
            self.password_manager.delete_password(password_id)
            print('Password deleted!')
        except KeyboardInterrupt:
            print('Interrupted by user!')
            return

    def update_password(self):
        try:
            password_id = input('Enter password id: ')
            if password_id == '':
                print('Password id is required!')
                return

            password_obj = self.password_manager.get_password_by_id(password_id)
            name = input(f'Enter the name ({password_obj[1]}): ')
            if name == '':
                name = password_obj[1]
            else:
                if self.password_manager.get_password_by_name(name) and name != password_obj[1]:
                    print(f'Password already exists! (name is {name})')
                    return
            original_login_name = self.password_manager.aes_decrypt(password_obj[2])
            login_name = input(f'Enter the login name ({original_login_name}): ')
            if login_name == '':
                login_name = password_obj[2]
            password = input('Enter the password: ')
            if password == '':
                password = self.password_manager.aes_decrypt(password_obj[3])
            memo = input(f'\n\n({password_obj[4]})\n\nEnter the memo: ')
            if memo == '':
                memo = password_obj[4]
            url = input(f'Enter the url ({password_obj[5]}): ')
            if url == '':
                url = password_obj[5]

            if url != '' and not self.is_valid_url(url):
                while True:
                    url = input('Invalid url! Please enter a valid url: ')
                    if self.is_valid_url(url):
                        break

            self.password_manager.update_password(password_id, name, login_name, password, memo, url)
            print('Password updated!')
        except KeyboardInterrupt:
            print('Interrupted by user!')
            return

    def list_files(self):
        print(f'database file: {self.conf_utils.get("db", "database_file")}')
        print(f'configuration file: {self.conf_utils.config_file}')

    def backup_db(self):
        backup_file = input('Please enter the backup file path and file name (the default location is in the same folder as the database file): ')
        if backup_file == '':
            backup_file = self.password_manager.backup_db()
        else:
            backup_file = self.password_manager.backup_db(backup_file)
        print(f'Database file backed up to {backup_file}')

    def upload(self):
        if self.check_api_token():
            result = self.password_manager.upload_db()
            if result.status_code == 200:
                # todo: need to check the server response a valid message
                print(f'Database file uploaded to cloud! {result.text}')
                print(f'API url: {self.conf_utils.get("common", "cloud_api")}')
            else:
                print(f'Upload failed! {result.status_code} {result.text}')
                print(f'API url: {self.conf_utils.get("common", "cloud_api")}')

    def restore(self):
        if self.check_api_token():
            url = self.conf_utils.get('common', 'cloud_api')
            confirm = input(f'Are you sure you want to restore the database file from the cloud service? \nPlease ensure that the API URL provided is valid: {url} (Y/n): ')
            if confirm == 'Y':
                result = self.password_manager.restore_db()
                if result.status_code == 200:
                    print(f'Database file restored!')
                    print(f'API url: {self.conf_utils.get("common", "cloud_api")}')
                    print(f'Database file path: {self.conf_utils.get("db", "database_file")}')
                else:
                    print(f'Restored failed! {result.status_code} {result.text}')
                    print(f'API url: {self.conf_utils.get("common", "cloud_api")}')

    def show_password(self, selected_password):
        print('+++++++++++++++++++++++++++++++')
        password = self.password_manager.aes_decrypt(selected_password[3])
        login_name = self.password_manager.aes_decrypt(selected_password[2])
        print(f'\nlogin name: {login_name}')
        print(f'password: {password} \n\n')
        print(f'id: {selected_password[0]}')
        print(f'name: {selected_password[1]}')
        print(f'url: {selected_password[5]}')
        print(f'memo: {selected_password[4]}\n')
        print('+++++++++++++++++++++++++++++++')

    def check_api_token(self):

        try:
            url = self.conf_utils.get('common', 'cloud_api')
            token = self.conf_utils.get('common', 'cloud_token')
            return True
        except (configparser.NoOptionError, configparser.NoSectionError):
            return self.set_api_token()

    def set_api_token(self):
        try:
            url = input('Enter the cloud API url: ')
            if url == '':
                print('Cloud API url is required!')
                return False

            if not self.is_valid_url(url):
                print('Invalid url!')
                return False

            token = input('Enter the cloud API token: ')
            if token == '':
                print('Cloud API token is required!')
                return False

            self.conf_utils.set('common', 'cloud_api', url)
            self.conf_utils.set('common', 'cloud_token', token)
        except KeyboardInterrupt:
            print('Interrupted by user!')
            return False

        return True

    @staticmethod
    def is_valid_url(url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

