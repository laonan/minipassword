# Mini Password


## Description
Mini Password is a command-line password manager. It is a simple and lightweight password manager that can be used in the command line or in the code. It is based on the SQLite database and the configuration file. It is easy to use and easy to deploy. It is suitable for personal use or small teams. It is written in Python and can be used in any platform that supports Python.

The `login name` and `password` are encrypted using the AES algorithm, and the secret key is stored in the configuration file. You should keep the configuration file in a safe place and avoid backing up the SQLite database file and the secret key together.

## Installation
   
    pip install minipassword

If you want to install it directly on the system (such as a device like Raspberry Pi) rather than in a virtual environment, you probably need to add the configuration to the ~/.config/pip/pip.conf file:

    [global]
    break-system-packages = true

If encounter the error `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'. Did you mean: 'zipimporter'?` in python 3.12, you can try:

    python -m ensurepip --upgrade
    python -m pip install --upgrade setuptools
    pip3 install --upgrade pip

    
## Usage in code
    
    from minipassword.box import ConfUtils, PasswordManager
    
    # initialize the configuration file and database file
    conf = ConfUtils()
    conf.create_config_file()
    
    # add a password
    pm = PasswordManager()
    pm.add_password('Google Account', 'account@gmail.com', 'youramazingpassword', 'memo')

    # query passwords
    result = pm.query_password('Google')
    print(result)

    # get all passwords
    result = pm.get_all_passwords()

    # get a password by id
    password_id = 1
    result = pm.get_password_by_id(password_id)

    # get passwords by name
    result = pm.get_passwords_by_name('Google')

    # delete a password, get password_id from the query_password method
    password_id = 1
    pm.delete_password(password_id)
    
    # update a password, get password_id from the query_password method
    password_id = 1
    pm.update_password(password_id, 'Google', 'newpassword', 'newmemo')
  

# Usage in command line
In this way, you should create a simple executable file to use the library.
for example, create a file named `mm` with the following content:

```python
#!/usr/bin/env python
from minipassword.commands import CommandHandler
h = CommandHandler()

if __name__ == '__main__':
   h.run()
```

then, you should make the file executable:

```bash
$ chmod +x mm
```

and move the file to a directory in your PATH  `/usr/local/bin`:

```bash
$ mv mm /usr/local/bin
```

now you can use the command line like this:

## Query  password
```
    $ mm
    $ Enter a query string:: Google
    +++++++++++++++++++++++++++++++

    login name: name@google.com
    password: myfancygooglepassword
    
    
    id: 1
    name: Google Account
    url: https://www.google.com
    memo: Google Account
    
    +++++++++++++++++++++++++++++++
```

More commands please see the help below:

# Commands help:

```
# if the custom command still is `mm`
$ mm -h
usage: testcommands.py [-h] [-a] [-d] [-u] [-l] [-b] [-p] [-r] [-api] [-dd]

Mini Password is a command-line password manager.

options:
  -h, --help       show this help message and exit
  -a, --add        add a new password
  -d, --delete     delete a password
  -u, --update     update a password
  -l, --list-file  list database file and configuration file paths
  -b, --backup     backup the database file
  -p, --upload     upload the database file to a cloud service
  -r, --restore    restore the database file from cloud service
  -api, --api      set cloud API url and token
  -dd, --destroy   destroy the database, all data will be lost!

```


## Issues
https://github.com/laonan/minipassword/issues
