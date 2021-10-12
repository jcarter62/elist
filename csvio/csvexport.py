from db import DB
import csv
import os
import tempfile


class csvExport:
    _temp_folder = ''

    def __init__(self):
        self._temp_folder = tempfile.TemporaryDirectory()
        foldername = self._temp_folder.name
        if not os.path.exists(foldername):
            os.path.mkdir(foldername)
        return

    def __del__(self):
        self._temp_folder.cleanup()
        return

    #
    # csvExport employee records, and pass back
    # file name
    #
    def execute(self) -> str:

        file_name = os.path.join(self._temp_folder.name, 'employees.csv')
        data = DB()
        employees = data.load_employees()
        with open(file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(['first_name', 'last_name', 'desk_phone', 'mobile_phone',
                                 'email', 'title', 'empid', 'location', 'start_date', 'end_date'])
            for row in employees:
                csv_writer.writerow([row['first_name'], row['last_name'], row['desk_phone'], row['mobile_phone'], row['email'], row['title'], row['empid'], row['location'], row['start_date'], row['end_date']])
        return file_name

