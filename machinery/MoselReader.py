import datetime
import urllib.request
from urllib.error import URLError
from bs4 import BeautifulSoup
from pathlib import Path
import json

#_URL = "http://www.bafg.de/DE/06_Info_Service/02_GewGuete/gewaesserguete_node.html"
_URL = "http://www.bafg.de/php/pkoblenz.htm"
_CACHE_FILE = "data/mosel_cache.json"
_TS_FORMAT = "%d.%m.%Y %H:%M"

def debugp(msg):
    if False:
        print(msg)

def _json_to_moselwerte(json):
    moselwerte = {}
    moselwerte['timestamp'] = json['timestamp']
    moselwerte['temp'] = json['temp']
    moselwerte['hoehe'] = json['hoehe']
    moselwerte['sauerstoff'] = json['sauerstoff']
    moselwerte['phwert'] = json['phwert']
    moselwerte['leitf'] = json['leitf']
    moselwerte['truebung'] = json['truebung']
    return moselwerte

def _is_valid(moselwerte):
    valid = not (int(float(moselwerte['hoehe'].split(' ')[0])) == 0 and int(float(moselwerte['truebung'].split(' ')[0])) == 0)
    return valid

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def _calc_mean(temp1, temp2, temp3):
    n = 0
    mean = 0.0
    if not isclose(temp1, 0.0):
        mean += temp1
        n += 1
    if not isclose(temp2, 0.0):
        mean += temp2
        n += 1
    if not isclose(temp3, 0.0):
        mean += temp3
        n += 1

    if n == 0:
        return -99
    debugp("%s, %s, %s, = %s" % (temp1, temp2, temp3, mean/n))
    return mean / n

def _readwww():
    # fetch html
    fp = urllib.request.urlopen(_URL)
    html_bytes = fp.read()
    html = html_bytes.decode('utf8')
    fp.close()

    # parse html
    soup = BeautifulSoup(html, 'lxml')
    mosel_table = soup.find_all('table')[1]
    rows = mosel_table.find_all('tr')

    hoehe       = "%.1f cm"    % float(rows[1].find_all('td')[7].get_text())
    sauerstoff  = "%.1f mg/l"  % float(rows[3].find_all('td')[7].get_text())
    phwert      = "%.1f pH"    % float(rows[4].find_all('td')[7].get_text())
    leitf       = "%.1f uS/cm" % float(rows[5].find_all('td')[7].get_text())
    truebung    = "%.1f TE/F"  % float(rows[6].find_all('td')[7].get_text())

    temp17      = float(rows[2].find_all('td')[4].get_text())
    temp23      = float(rows[2].find_all('td')[5].get_text())
    temp05      = float(rows[2].find_all('td')[7].get_text())
    temp        = _calc_mean(temp17, temp23, temp05)

    timestamp   = datetime.datetime.now().strftime(_TS_FORMAT)

    moselwerte = {}
    moselwerte['temp']=temp
    moselwerte['hoehe']=hoehe
    moselwerte['sauerstoff']=sauerstoff
    moselwerte['phwert']=phwert
    moselwerte['leitf']=leitf
    moselwerte['truebung']=truebung
    moselwerte['timestamp'] = timestamp
    debugp('read from www: %s' % moselwerte)
    return moselwerte

def _build_error(code, msg):
    error = {}
    error['code'] = code
    error['msg'] = msg
    error['timestamp'] = datetime.datetime.now().strftime(_TS_FORMAT)
    return error

def do_magic():
    # look into cache
    moselwerte_cache = None
    cache_exists = Path(_CACHE_FILE).is_file()
    # handle if cache doesn't exist
    if cache_exists:
        debugp('cache exists')
        json_data = json.load(open(_CACHE_FILE))
        moselwerte_cache = _json_to_moselwerte(json_data)
        moselwerte_cache['code'] = 0

    # if cache date is still valid
        cache_date = datetime.datetime.strptime(moselwerte_cache['timestamp'], _TS_FORMAT)
        now = datetime.datetime.now()
        delta = datetime.timedelta(hours=5)
        debugp(now - delta)
        if cache_date > now - delta:
            # use cached data
            debugp('got current cache data')
            return moselwerte_cache

    # read www
    try:
        moselwerte = _readwww()
    except Exception as e:
    #except (ConnectionError, URLError) as e:
        return _build_error(2, 'Die Moselwerte konnten nicht gelesen werden ' + str(e))

    # is www valid?
    if _is_valid(moselwerte):
        moselwerte['code'] = 0 # errorcode 0: no error
        # write cache
        debugp('writing cache')
        with open(_CACHE_FILE, 'w') as outfile:
            json.dump(moselwerte, outfile)
        return moselwerte

    # cache not valid - cache existed?
    if cache_exists:
        return moselwerte_cache

    # no cache exists and www is invalid: return error
    return _build_error(1, 'Die Moselwerte konnten nicht gelesen werden.')


if __name__ == "__main__":
    moselwerte = do_magic()
    print(moselwerte)
