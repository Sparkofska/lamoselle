from BaseTableManager import BaseTableManager
from RankingTableManager import RankingTableManager
import datetime

tm = RankingTableManager()
tm.create_table_if_not_exists()

now = datetime.datetime.now()
now_insert = now.strftime(BaseTableManager.DATETIME_STRING_FORMAT)

tm.insert_tuple((now_insert, 'username', '12', '13'))

l = tm.read_all()

for i in l:
    print(i)
