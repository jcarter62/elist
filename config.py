import os

SECRET_KEY = '5 blue trees and 3 pink eagles'

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'C:\\ProgramData\\wwd\\elist.sqlite3')
IMAGE_PATH = os.environ.get('IMAGE_PATH', 'C:\\ProgramData\\wwd\\elist.images')
