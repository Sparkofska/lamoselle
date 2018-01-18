import datetime
import urllib.request
from urllib.error import URLError
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import configparser

_CONFIG_FILE = "data/config.txt"
_CACHE_FILE = "data/weather_cache.json"
_TS_FORMAT = "%d.%m.%Y %H:%M"

def debugp(msg):
    if True:
        print(msg)

def __get_url():
    url = "http://api.openweathermap.org/data/2.5/weather?"
    url += "id=2886946" # Koblenz
    url += "&units=metric" # Celcius
    url += "&lang=de" # use de for german

    config = configparser.ConfigParser()
    config.read(_CONFIG_FILE)
    url += "&APPID=" + config['APPID']['APPID'] # API key from openweathermap.org
    debugp('url: ' + url)
    return url

def _is_valid(weather):
    return weather['cod'] == 200

def _cache_to_weather(json):
    weather = {}
    weather['timestamp'] = json['timestamp']
    weather['cod'] = json['cod']
    weather['city'] = json['city']
    weather['id'] = json['id']
    weather['main'] = json['main']
    weather['description'] = json['description']
    weather['icon'] = json['icon']
    weather['temp'] = json['temp']
    weather['humidity'] = json['humidity']
    weather['wind'] = json['wind']
    weather['clouds'] = json['clouds']
    weather['sunset'] = json['sunset']
    weather['date'] = json['date']
    return weather

def _www_to_weather(json):
    cod = json['cod']
    if cod != 200 :
        message = json['message']
        return {'cod':cod, 'message':message}
    else:
        result = {'cod':cod}

        result['city'] = json['name']
        result['id'] = json['weather'][0]['id'] # weather id as specified in https://openweathermap.org/weather-conditions
        result['main'] = json['weather'][0]['main'] # category of weather
        result['description'] = json['weather'][0]['description']
        result['icon'] = json['weather'][0]['icon']
        result['temp'] = json['main']['temp'] # in °C
        result['humidity'] = json['main']['humidity'] # in %
        result['wind'] = json['wind']['speed'] # in m/s
        result['clouds'] = json['clouds']['all'] # cloudiness in %
        result['sunset'] = datetime.datetime.utcfromtimestamp(json['sys']['sunset']).strftime('%H:%M Uhr') # Time of data calculation, unix, UTC
        result['date'] = datetime.datetime.utcfromtimestamp(json['dt']).strftime('%d.%m.%Y %H:%M') # Time of data calculation, unix, UTC

        result['timestamp'] = datetime.datetime.now().strftime(_TS_FORMAT) # Timestamp of writing cache
        return result

def _readwww():
    data = requests.get(__get_url()).json()
    return _www_to_weather(data)

def _build_error(code, msg):
    error = {}
    error['code'] = code
    error['msg'] = msg
    error['timestamp'] = datetime.datetime.now().strftime(_TS_FORMAT)
    return error

def do_magic():
    # look into cache
    weather_cache = None
    cache_exists = Path(_CACHE_FILE).is_file()
    # handle if cache doesn't exist
    if cache_exists:
        debugp('cache exists')
        json_data = json.load(open(_CACHE_FILE))
        weather_cache = _cache_to_weather(json_data)
        weather_cache['code'] = 0

    # if cache date is still valid
        cache_date = datetime.datetime.strptime(weather_cache['timestamp'], _TS_FORMAT)
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=30)
        debugp(now - delta)
        if cache_date > now - delta:
            # use cached data
            debugp('got current cache data')
            return weather_cache

    # read www
    try:
        weather = _readwww()
    except Exception as e:
        #except (ConnectionError, URLError) as e:
        return _build_error(2, 'Die Wetterdaten konnten nicht gelesen werden. ' + str(e))

    # is www valid?
    if _is_valid(weather):
        weather['code'] = 0 # errorcode 0: no error
        # write cahe
        debugp('writing cache')
        with open(_CACHE_FILE, 'w') as outfile:
            json.dump(weather, outfile)
        return weather

    # cache not valid - cache existed?
    if cache_exists:
        return weather_cache

    # no cache exists and www is invalid: return error
    return _build_error(1, 'Die Wetterdaten konnten nicht gelesen werden.')


if __name__ == "__main__":
    weather = do_magic()
    print(weather)
