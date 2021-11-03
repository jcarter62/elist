import sqlite3
from flask import current_app
from sqlite3 import Error
import arrow
import pymongo


class DB:
    # ref: https://www.sqlitetutorial.net/sqlite-python/create-tables/
    _curapp = None
    _dbpath = None
    _conn = None
    _maxid = 0

    def __init__(self):
        self._curapp = current_app
        self._get_settings()
        self._conn = self._create_connection()
        self._create_employees_table()
        if self._employee_records() <= 0:
            self._create_empty_employees()
            newid = self._get_next_id()
            self.insert_employee(id=newid, first_name='Joe', last_name='User')
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

    def _create_employees_table(self):
        try:
            c = self._conn.cursor()
            cmd = """CREATE TABLE IF NOT EXISTS employees (
                        id integer PRIMARY KEY,
                        first_name text NOT NULL,
                        last_name text NOT NULL,
                        desk_phone text,
                        mobile_phone text,
                        email text,
                        title text,
                        empid text,
                        location text,
                        start_date text,
                        end_date text,
                        image text
                    );"""
            c.execute(cmd)
        except Error as e:
            print(e)
        return

    def _employee_records(self):
        # ref https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
        num = 0
        try:
            c = self._conn.cursor()
            cmd = 'Select count(*) from employees;'
            c = c.execute(cmd)
            rows = c.fetchall()

            for row in rows:
                num = num + row[0]
        except Error as e:
            print(e)
        return num

    def _get_next_id(self):
        id = 0
        try:
            c = self._conn.cursor()
            cmd = 'select max(id) from employees;'
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

    def _create_empty_employees(self):
        try:
            c = self._conn.cursor()
            newid = self._get_next_id()
            cmd1 = 'insert into employees (id, first_name, last_name) values (newid, "first", "last");'
            cmd2 = 'delete from employees where id = newid;'
            c.execute(cmd1)
            c.execute(cmd2)
            self._commit()

        except Error as e:
            print(e)
        return

    def _years_of_service(self, start_date, end_date):

        result = 0.0
        if start_date is None or start_date <= '':
            # can't calculate.
            pass
        else:
            if end_date is None or end_date <= '':
                end_date = arrow.now()
            else:
                end_date = arrow.get(end_date)

            start_date = arrow.get(start_date, 'MM/DD/YYYY')

            try:
                diff_date = end_date - start_date
                result = diff_date.days / 365.25
            except:
                result = 0.0

        result = '{:.2f}'.format(result)
        return result

    def insert_employee(self, id, first_name='', last_name='', desk_phone='', mobile_phone='', email='', title='',
                        empid='', location='', start_date='', end_date='', image=''):
        try:
            cmd = 'insert into employees ' + \
                  '(id, first_name, last_name, desk_phone, mobile_phone, email, title, empid, location, start_date, end_date, image) ' + \
                  'values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            c = self._conn.cursor()
            params = (id, first_name, last_name, desk_phone, mobile_phone,
                      email, title, empid, location, start_date, end_date, image)
            c.execute(cmd, params)
            self._commit()
        except Error as e:
            print(e)
        return

    def load_employees(self) -> []:
        data = []
        try:
            cmd = 'select id, first_name, last_name, desk_phone, mobile_phone, ' + \
                  'email, title, empid, location, start_date, end_date, image from employees;'
            c = self._conn.cursor()
            c = c.execute(cmd)
            rows = c.fetchall()

            for row in rows:
                yofs = self._years_of_service(row[9], row[10])
                one = {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "name": row[1] + ' ' + row[2],
                    "desk_phone": row[3],
                    "mobile_phone": row[4],
                    "email": row[5],
                    "title": row[6],
                    "empid": row[7],
                    "location": row[8],
                    "start_date": row[9],
                    "end_date": row[10],
                    "image": row[11],
                    "yofs": yofs
                }
                data.append(one)

        except Error as e:
            print(e)
        return data

    def load_employee(self, empid) -> []:
        data = {}
        try:
            cmd = 'select id, first_name, last_name, desk_phone, mobile_phone, ' + \
                  'email, title, empid, location, start_date, end_date, image from employees ' + \
                  'where empid = ? ;'
            c = self._conn.cursor()
            c = c.execute(cmd, [empid])
            rows = c.fetchall()

            for row in rows:
                yofs = self._years_of_service(row[9], row[10])
                data = {
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "name": row[1] + ' ' + row[2],
                    "desk_phone": row[3],
                    "mobile_phone": row[4],
                    "email": row[5],
                    "title": row[6],
                    "empid": row[7],
                    "location": row[8],
                    "start_date": row[9],
                    "end_date": row[10],
                    "image": row[11],
                    "yofs": yofs
                }

        except Error as e:
            print(e)
        return data

    def update_employee(self, data):
        try:
            cmd = 'update employees set first_name = ?, last_name = ?, desk_phone = ?, mobile_phone = ?, ' + \
                  'email = ?, title = ?, empid = ?, location = ?, start_date = ?, end_date = ?, image = ? ' + \
                  'where id = ?;'
            c = self._conn.cursor()
            params = (data['first_name'], data['last_name'], data['desk_phone'], data['mobile_phone'],
                      data['email'], data['title'], data['empid'], data['location'], data['start_date'],
                      data['end_date'], data['image'], data['id'])
            c = c.execute(cmd, params)
            self._commit()

        except Error as e:
            print(e)
        return

    def create_new_employee(self) -> int:
        newid = self._get_next_id()
        self.insert_employee(id=newid, first_name='', last_name='')
        return newid

    def load_from_array(self, data):
        max_id = 0

        # Truncate table
        try:
            c = self._conn.cursor()
            cmd = 'delete from employees;'
            c.execute(cmd)
            self._commit()
        except Error as e:
            print(e)

        # get max id
        try:
            cmd = 'select max(id) as num from systems;'
            c = self._conn.cursor()
            c = c.execute(cmd)
            row = c.fetchone()

            max_id = row[0]
            if max_id is None:
                max_id = 0
        except Error as e:
            print(e)

        # Iterate data
        new_id = max_id
        for row in data:
            new_id = new_id + 1
            self.insert_employee(id=new_id, first_name=row['first_name'], last_name=row['last_name'],
                                 desk_phone=row['desk_phone'], mobile_phone=row['mobile_phone'],
                                 email=row['email'], title=row['title'], empid=row['empid'], location=row['location'],
                                 start_date=row['start_date'], end_date=row['end_date'])

        return

    def delete_employee(self, empid) -> []:
        try:
            cmd = 'delete from employees where empid = ? ;'
            c = self._conn.cursor()
            c.execute(cmd, [empid])
            self._commit()
        except Error as e:
            print(e)
        return
