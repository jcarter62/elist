import pymongo
from flask import current_app
from pymongo import MongoClient, errors
import arrow


class MDB:
    _client = None
    _host = None
    _db = None
    _collection_name = 'employees'
    _date_formats = ['MM/DD/YYYY', 'YYYY-MM-DD']

    def __init__(self):
        self._db = current_app.config['MONGODB_DB']
        self._host = current_app.config['MONGODB_HOST']
        self._client = MongoClient(self._host, 27017)

    def _collection(self):
        return self._client[self._db][self._collection_name]

    def _years_of_service(self, start_date, end_date):
        import pandas as pd
        result = 0.0
        if start_date is None or start_date <= '':
            pass
        else:
            if (end_date is None) or pd.isna(end_date) or (end_date == ''):
                end_date = arrow.now()
            else:
                end_date = arrow.get(end_date)

            start_date = arrow.get(start_date, self._date_formats)

            try:
                diff_date = end_date - start_date
                result = diff_date.days / 365.25
            except:
                result = 0.0
        result = '{:.2f}'.format(result)
        return result

    def insert_employee(self, rec_id, first_name='', last_name='', desk_phone='', mobile_phone='', email='', title='',
                        empid='', location='', start_date='', end_date='', image=''):
        try:
            obj = {
                '_id': rec_id, 'first_name': first_name, 'last_name': last_name, 'desk_phone': desk_phone,
                'mobile_phone': mobile_phone, 'email': email, 'title': title, 'empid': empid, 'location': location,
                'start_date': start_date, 'end_date': end_date
            }
            employees = self._collection()
            employees.insert_one(obj)
        except errors.PyMongoError as e:
            print(e)
        return

    def right(self, value, count):
        return value[-count:]

    #
    # convert date to YYYY-MM-DD
    #
    def convert_date(self, dt):
        import datetime
        year = arrow.get(dt, self._date_formats).datetime.year
        month = arrow.get(dt, self._date_formats).datetime.month
        day = arrow.get(dt, self._date_formats).datetime.day
        result = str(year) + '-' + self.right('0' + str(month), 2) + '-' + self.right('0' + str(day), 2)
        return result

    def format_phone(self, value):
        if type(value) == type('str'):
            if value <= '':
                return '--'
        else:
            return '--'
        return value

    def load_employees(self) -> []:
        data = []
        try:
            for emp in self._collection().find():
                one = emp
                one['yofs'] = self._years_of_service(one['start_date'], one['end_date'])
                one['name'] = one['first_name'] + ' ' + one['last_name']
                one['start_date_str'] = self.convert_date(one['start_date'])
                one['desk_phone'] = self.format_phone(one['desk_phone'])
                one['mobile_phone'] = self.format_phone(one['mobile_phone'])

                data.append(one)
        except errors.PyMongoError as e:
            print(e)
        return data

    def myint(self, value) -> int:
        try:
            if type(value) == type('str'):
                result = int(value)
            else:
                result = value
        except Exception as e:
            print(e)
            result = value
        return result

    def load_employee(self, empid=0) -> object:
        data = {}
        empid_int = self.myint(empid)

        if empid_int > 0:
            try:
                all = self.load_employees()
                for emp in all:
                    if self.myint(emp['empid']) == empid_int:
                        data = emp
            finally:
                pass

        return data

    def update_employee(self, rec_id, first_name='', last_name='', desk_phone='', mobile_phone='', email='', title='',
                        empid='', location='', start_date='', end_date='', image=''):
        try:
            obj = {
                '_id': rec_id, 'first_name': first_name, 'last_name': last_name, 'desk_phone': desk_phone,
                'mobile_phone': mobile_phone, 'email': email, 'title': title, 'empid': empid, 'location': location,
                'start_date': start_date, 'end_date': end_date
            }
            employees = self._collection()
            employees.update_one({'_id': rec_id}, {'$set': obj}, upsert=False)
        except errors.PyMongoError as e:
            print(e)
        return

    def update_employee_by_obj(self, emp: object):
        try:
            obj = {
                '_id': emp['_id'], 'first_name': emp['first_name'], 'last_name': emp['last_name'],
                'desk_phone': emp['desk_phone'],
                'mobile_phone': emp['mobile_phone'], 'email': emp['email'], 'title': emp['title'],
                'empid': emp['empid'], 'location': emp['location'],
                'start_date': emp['start_date'], 'end_date': emp['end_date']
            }
            employees = self._collection()
            employees.update_one({'_id': emp['_id']}, {'$set': obj}, upsert=False)
        except errors.PyMongoError as e:
            print(e)
        return

    def load_from_array(self, data):
        max_id = 0

        employees = self._collection()

        # Truncate table
        try:
            employees.delete_many({})
        except errors.PyMongoError as e:
            print(e)

        # get max id
        try:
            obj = employees.find_one({}, sort=[('_id', pymongo.DESCENDING)])
            if obj is None:
                max_id = 0
            else:
                max_id = obj['_id']
        except errors.PyMongoError as e:
            print(e)

        # Iterate data
        new_id = max_id
        for row in data:
            new_id = new_id + 1
            self.insert_employee(rec_id=new_id, first_name=row['first_name'], last_name=row['last_name'],
                                 desk_phone=row['desk_phone'], mobile_phone=row['mobile_phone'],
                                 email=row['email'], title=row['title'], empid=row['empid'], location=row['location'],
                                 start_date=row['start_date'], end_date=row['end_date'])

        return

    def delete_employee(self, empid) -> []:
        try:
            employees = self._collection()
            employees.deleteOne({'empid': empid})
        except errors.PyMongoError as e:
            print(e)
        return
