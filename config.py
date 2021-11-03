import os

# SECRET_KEY = os.environ.get('SECRET_KEY', '5 blue trees and 3 pink eagles')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'C:\\ProgramData\\wwd\\elist.sqlite3')
IMAGE_PATH = os.environ.get('IMAGE_PATH', 'C:\\ProgramData\\wwd\\elist.images')

# SESSION_DB = os.environ.get('SESSION_DB', 'sqlite:///C:\\projects\\elist\\data\\session.sqlite')
# SESSION_TYPE = 'sqlalchemy'
# SESSION_DB = os.environ.get('SESSION_DB', 'C:\\projects\\elist\\data\\sessions')
# SESSION_TYPE = 'filesystem'
# SESSION_FOLDER = os.environ.get('SESSION_FOLDER', 'C:\\projects\\elist\\data\\sessions')
# SESSION_FOLDER = os.environ.get('SESSION_FOLDER', 'C:\\ProgramData\\wwd\\elist\\data\\sessions')

SESSION_TYPE = 'mongodb'
SESSION_MONGODB_DB = 'E-List'
SESSION_MONGODB_COLLECT = 'sessions'

MONGODB_DB = 'EList'
MONGODB_HOST = 'localhost'

