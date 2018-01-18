from machinery.BaseTableManager import BaseTableManager
#from machinery.BaseTableManager import BaseTableManager
import datetime

class RankingTableManager(BaseTableManager):

    TABLE_NAME = "ranking"

    _COL_TIMESTAMP = 'timestamp'
    _COL_NAME = 'name'
    _COL_SCORE = 'score'
    _COL_TEMP = 'temp'

    def __init__(self):
        BaseTableManager.__init__(self)
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = self.get_db()
        c = conn.cursor()
        c.execute(('''CREATE TABLE IF NOT EXISTS {0} (
            ''' + self._COL_TIMESTAMP + ''' TEXT,
            ''' + self._COL_NAME + ''' TEXT,
            ''' + self._COL_SCORE + ''' INTEGER,
            ''' + self._COL_TEMP + ''' INTEGER
            )''').format(self.TABLE_NAME))
        conn.commit()
        self.close_db()

    def insert_tuple(self, ranking_tuple):
        conn = self.get_db()
        c = conn.cursor()

        c.execute('''INSERT INTO %s VALUES
            (?, ?, ?, ?)
            ''' % self.TABLE_NAME, ranking_tuple)

        conn.commit()
        self.close_db()

    def insert_dict(self, ranking_dict):
        tup = (
                ranking_dict[self._COL_TIMESTAMP],
                ranking_dict[self._COL_NAME],
                ranking_dict[self._COL_SCORE],
                ranking_dict[self._COL_TEMP]
                ) 
        self.insert_tuple(tup)

    def read_all(self):
        conn = self.get_db()
        c = conn.cursor()

        c.execute('''SELECT * FROM %s
            ''' % self.TABLE_NAME)

        l = []
        for row in c:
            l.append(self.to_dict(row))

        conn.commit()
        self.close_db()

        return l

    def read_all_by_user(self, username):
        conn = self.get_db()
        c = conn.cursor()

        stmt = '''SELECT * FROM %s WHERE %s = ? ''' % (self.TABLE_NAME, self._COL_NAME)
        c.execute(stmt, (username,))

        l = []
        for row in c:
            l.append(self.to_dict(row))

        conn.commit()
        self.close_db()
        return l

    def read_latest_by_user(self, username):
        al = self.read_all_by_user(username)
        if not al: # list is empty
            return None
        al.sort(key=lambda x: x[self._COL_TIMESTAMP], reverse=True)
        return al[0]

    def _cummulate(self, rows):
        cummulated = {'score':0, 'times':0}
        cummulated['name'] = None
        cummulated['newest_date'] = datetime.datetime(year=2000, month=1, day=1) # way in the past
        cummulated['newest_temp'] = 0.0
        cummulated['min_date'] = None
        cummulated['min_temp'] = +1000.0
        cummulated['max_date'] = None
        cummulated['max_temp'] = -1000.0

        for row in rows:
            date = datetime.datetime.strptime(row[self._COL_TIMESTAMP], BaseTableManager.DATETIME_STRING_FORMAT)
            temp = row[self._COL_TEMP]
            score = row[self._COL_SCORE]
            cummulated['score'] += score
            cummulated['times'] += 1

            if cummulated['name'] is None:
                cummulated['name'] = row['name']
            else:
                if cummulated['name'] != row['name']:
                    raise RuntimeError("Wrong call of method. Only put rows of one username as parameter.")

            if date > cummulated['newest_date']:
                cummulated['newest_date'] = date
                cummulated['newest_temp'] = temp

            if temp < cummulated['min_temp']:
                cummulated['min_temp'] = temp
                cummulated['min_date'] = date

            if temp > cummulated['max_temp']:
                cummulated['max_temp'] = temp
                cummulated['max_date'] = date

        return cummulated

    def read_cummulated_by_user(username):
        l = read_all_by_user(username)
        return _cummulate(l)

    def read_all_cummulated_sorted(self):
        rows = self.read_all()
        cummulated = {}
        for row in rows:
            user_rows = cummulated.get(row['name'], [])
            user_rows.append(row)
            cummulated[row['name']] = user_rows

        # cummulate users
        result = []
        for key, user_rows in cummulated.items():
            result.append(self._cummulate(user_rows))

        # sorting by scored
        result.sort(key=lambda x: x['score'], reverse=True)
        # adding the rank to the output
        for i, entry in enumerate(result):
            entry['rank'] = i+1

        return result

    def to_dict(self, ranking_tuple):
        return {
                self._COL_TIMESTAMP : ranking_tuple[0],
                self._COL_NAME : ranking_tuple[1],
                self._COL_SCORE : ranking_tuple[2],
                self._COL_TEMP : ranking_tuple[3]
                }


if __name__ == "__main__":
    tm = RankingTableManager()
    #l = tm.read_by_username('Sparkofska')
    l = tm.read_all_cummulated_sorted()
    for i in l:
        print(i)
