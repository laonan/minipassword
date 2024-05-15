import os
import json
import time
import argparse
import sqlite3
from minipassword.box import PasswordManager

# Create the parser
parser = argparse.ArgumentParser(description='Process a JSON file.')

# Add the arguments
parser.add_argument('FilePath', metavar='filepath', type=str, help='the path to the JSON file')

# Parse the arguments
args = parser.parse_args()

seed_file = 'importseed'

if not os.path.isfile(seed_file):
    with open(seed_file, 'w') as f:
        f.write('0')


with open(seed_file, 'r') as f:
    seed = int(f.read())


# Open the JSON file
with open(args.FilePath, 'r') as file:
    # Load JSON data from file
    data = json.load(file)

    if '企业邮箱' in data[seed]['name']:
        print('Importing 企业邮箱...')
        print(data[seed])
    else:
        print(f'Importing {data[seed]["name"]}...')

    try:
        pm = PasswordManager()
        pm.add_password(
            data[seed]['name'],
            data[seed]['login_name'],
            data[seed]['password'],
            data[seed]['memo'],
            data[seed]['url'],
        )

        seed += 1
        with open(seed_file, 'w') as f:
            f.write(str(seed))

        print(f'{data[seed]["name"]} imported successfully. seed = {seed}')

    except sqlite3.IntegrityError:
        seed += 1
        with open(seed_file, 'w') as f:
            f.write(str(seed))

        print(f'{data[seed]["name"]} already exists. seed = {seed}')
        pass





