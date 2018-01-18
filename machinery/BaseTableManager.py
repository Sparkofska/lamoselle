import sqlite3

class BaseTableManager():

    DATABASE_NAME = 'data/lamoselle.db'

    DATETIME_STRING_FORMAT = '%Y%m%d%H%M%S'

    def __init__(self):
        self._conn = None

    def get_db(self):
        '''
        opens a database connection and returns it
        '''
        if self._conn is None:
            self._conn = sqlite3.connect(self.DATABASE_NAME) 

        return self._conn

    def close_db(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = None

    def create_table_if_not_exists(self):
        raise NotImplementedError("Subclasses must implement this abstract method")

    def insert_tuple(self):
        raise NotImplementedError("Subclasses must implement this abstract method")

    def insert_dict(self):
        raise NotImplementedError("Subclasses must implement this abstract method")

    def read_all(self):
        raise NotImplementedError("Subclasses must implement this abstract method")

