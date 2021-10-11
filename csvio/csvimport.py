import pandas as pd

class csvImport:
    data = []

    def __init__(self):
        self.data = []

    def parseCSV(self, filePath):
        col_names = ['first_name', 'last_name', 'desk_phone', 'mobile_phone', 'email', 'title', 'empid',
                     'location', 'start_date', 'end_date']
        csvData = pd.read_csv(filePath, names=col_names, header=0)
        for i, row in csvData.iterrows():
            self.data.append(row)
            print(i, row)
        return self.data

