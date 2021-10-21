import hashlib
import hmac
import os
import sqlite3
from flask import current_app
from sqlite3 import Error


class DB:
    # ref: https://www.sqlitetutorial.net/sqlite-python/create-tables/
    _dbpath = None
    _conn = None
    _maxid = 0
    _table_name = 'users'
    _salt = 'testing 123'.encode()
    _pw_hash = None
    _user_id = 0
    _data = None

    def __init__(self, user_id=None):
        self._curapp = current_app
        self._get_settings()
        self._conn = self._create_connection()
        self._create_table()
        if self._table_records() <= 0:
            self._create_empty_table()
            self.insert_record(username="joe", password="pass")

        if user_id is None:
            pass
        else:
            # load user_id record, if it exists.
            self._user_id = user_id
            self._data = self.load_profile_record(self._user_id)
            if self._data is not None:
                self._pw_hash = self._data['password']
        return

    def _commit(self):
        if self._conn is not None:
            self._conn.commit()
        return

    def _get_settings(self):
        self._dbpath = self._curapp.config['DATABASE_PATH']

    def _create_connection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(self._dbpath)
            return conn
        except Error as e:
            print(e)
        return conn

    def _create_table(self):
        try:
            c = self._conn.cursor()
            cmd = 'create table if not exists ' + self._table_name + ' ( '
            cmd += 'id integer PRIMARY KEY, '
            cmd += 'username text NOT NULL, '
            cmd += 'password text NOT NULL, '
            cmd += 'email text NOT NULL, '
            cmd += 'admin text NULL );'

            c.execute(cmd)
        except Error as e:
            print(e)
        return

    def _table_records(self):
        # ref https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
        num = 0
        try:
            c = self._conn.cursor()
            cmd = 'Select count(*) from ' + self._table_name + ';'
            c = c.execute(cmd)
            rows = c.fetchall()

            for row in rows:
                num = num + row[0]

        except Error as e:
            print(e)
        return num

    def _get_next_id(self) -> int:
        id = 0
        try:
            c = self._conn.cursor()
            cmd = 'select max(id) from ' + self._table_name + ';'
            c = c.execute(cmd)
            row = c.fetchone()
            if row is None:
                id = 0
            else:
                id = row[0]
        except Error as e:
            print(e)
        id = id + 1
        return id

    def _create_empty_table(self):
        try:
            c = self._conn.cursor()
            newid = self._get_next_id()
            cmd1 = 'insert into employees (id, username, password) values (?, "name", "pass");'
            cmd2 = 'delete from employees where id = ?;'
            c.execute(cmd1, [newid])
            c.execute(cmd2, [newid])
            self._commit()

        except Error as e:
            print(e)
        return

    def insert_record(self, username='', password='', email='', admin=''):
        try:
            self.hash_new_password(password)
            id = self._get_next_id()
            cmd = 'insert into ' + self._table_name + ' ' + \
                  '(id, username, password, email, admin) ' + \
                  'values ( ?, ?, ?, ?, ?)'
            c = self._conn.cursor()
            params = (id, username, self._pw_hash, email, admin)
            c.execute(cmd, params)
            self._commit()
        except Error as e:
            print(e)
        return

    def load_record(self, username='', password='') -> []:
        data = None
        try:
            self.hash_new_password(password=password)

            cmd = 'select id, username, password, email, admin from ' + self._table_name +' ' +\
                'where username = ? and password = ? ;'
            c = self._conn.cursor()
            c = c.execute(cmd, [username, self._pw_hash])
            rows = c.fetchall()

            for row in rows:
                data = {
                    "id": row[0],
                    "username": row[1],
                    "password": row[2],
                    "email": row[3],
                    "admin": row[4]
                }

        except Error as e:
            print(e)
        return data

    def load_profile_record(self, user_id) -> object:
        data = None
        try:
            cmd = 'select id, username, email, admin, password from ' + self._table_name + ' ' +\
                'where id = ' + user_id + ';'
            c = self._conn.cursor()
            c = c.execute(cmd)
            rows = c.fetchall()

            for row in rows:
                data = {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "admin": row[3],
                    "password": row[4]
                }
        except Error as e:
            print(e)
        return data

    def update_profile_record(self, user_id, username, email):
        try:
            cmd = 'update ' + self._table_name + ' '
            cmd += 'set username = "' + username + '", '
            cmd += 'email = "' + email + '" '
            cmd += 'where id = ' + user_id + ';'
            c = self._conn.cursor()
            c = c.execute(cmd)
            self._commit()
        except Error as e:
            print(e)
        return

    def update_record(self, data):
        try:
            if data['password'] > '':
                self.hash_new_password(data['password'])


            cmd = 'update ? set id = ?, username = ?, password = ?, email = ?, admin = ? ' +\
                'where username = ?;'
            c = self._conn.cursor()
            params = ( self._table_name, data['id'], data['username'], self._pw_hash,
                       data['email'], data['admin'])
            c = c.execute(cmd, params)
            self._commit()

        except Error as e:
            print(e)
        return

    def delete_record(self, username):
        try:
            cmd = 'delete from ? where username = ? ;'
            c = self._conn.cursor()
            c.execute(cmd, [self._table_name, username])
            self._commit()
        except Error as e:
            print(e)
        return

    def save_password(self, user_id, password):
        try:
            self.hash_new_password(password)
            cmd = 'update ' + self._table_name + ' set password = "' + self._pw_hash + '" '
            cmd += 'where id = ' + user_id + ' ;'
            c = self._conn.cursor()
            c.execute(cmd)
            self._commit()

        except Error as e:
            print(e)
        return

    def hash_new_password(self, password: str):
        pwe = password.encode() + self._salt
        self._pw_hash = hashlib.sha256(pwe).hexdigest()
        return

    def hash_password(self, password: str) -> str :
        pwe = password.encode() + self._salt
        pw_hash = hashlib.sha256(pwe).hexdigest()
        return pw_hash

    def is_correct_password(self, password: str):
        pwe = password.encode() + self._salt
        pwhash = hashlib.sha256(pwe).hexdigest()
        if pwhash == self._pw_hash:
            return True
        else:
            return False
