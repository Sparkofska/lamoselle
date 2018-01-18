from machinery.BaseTableManager import BaseTableManager
from machinery.RankingTableManager import RankingTableManager
from machinery import MoselReader
import datetime
import json
import math
# from bs4 import BeautifulSoup

def calc_score(temp):
    if temp < -10:
        return 10
    return max(1, min(15, int((30-temp)/2.0)))

def insert_ranking(username):
    moselwerte = MoselReader.do_magic()
    #temp = int(float(moselwerte['temp'].split(' ')[0]))
    temp = int(moselwerte['temp'])
    score = calc_score(temp)

    now = datetime.datetime.now()
    now_insert = now.strftime(BaseTableManager.DATETIME_STRING_FORMAT)

    tm = RankingTableManager()
    latest_entry = tm.read_latest_by_user(username)
    if latest_entry is not None: # user exists in db
        today= datetime.datetime.now().date()
        last = datetime.datetime.strptime(latest_entry['timestamp'], RankingTableManager.DATETIME_STRING_FORMAT).date()
        print(today)
        print(last)
        if last >= today: # user already posted today
            print('NOT OK')
            return (-1, username + ' wurde heute schon eingetragen. Nicht schummeln!')

    print('OK')
    tm.insert_tuple((now_insert, username, score, temp))
    return (score, 'ok')

def get_ranking_html():
    tm = RankingTableManager()
    data = tm.read_all_cummulated_sorted() # list of dicts

    result = '<table id="moselranking">'
    result += '<thead><tr><th>#</th><th>Name</th><th>Badeg&auml;nge</th><th>Punkte</th><th>letzer Badegang</th><th>Temperatur</th></tr></thead><tbody>'

    for row in data:
        result += '<tr>'
        result += '<td>' + str(row['rank']) + '</td>'
        result += '<td>' + row['name'] + '</td>'
        result += '<td>' + str(row['times']) + '</td>'
        result += '<td>' + str(row['score']) + '</td>'
        result += '<td>' + row['newest_date'].strftime("%d.%m.%Y") + '</td>'
        result += '<td>' + str(row['newest_temp']) + '</td>'
        result += '</tr>'

    result += '</tbody></table>'
    return result

    # use this to prettyprint html
    # soup = BeautifulSoup(result, 'lxml')
    # return soup.prettify()

def get_ranking_json():
    tm = RankingTableManager()
    data = tm.read_all_cummulated_sorted()
    for row in data:
        row['newest_date'] = row['newest_date'].strftime("%Y.%m.%d %H:%M")
        row['min_date'] = row['min_date'].strftime("%Y.%m.%d %H:%M")
        row['max_date'] = row['max_date'].strftime("%Y.%m.%d %H:%M")

    result = '{"timestamp": "' + datetime.datetime.now().strftime("%Y.%m.%d %H:%M") + '",'
    result += '"ranking": '
    result += json.dumps(data)
    result += '}'
    return result

if __name__ == "__main__":
    #insert_ranking('Sparkofska')
    for x in range(-12, 30):
        print("%s : %s" % (x, calc_score(x)))
