from lamoselle import app
from flask import render_template, request, jsonify

from machinery import WeatherReader
from machinery import MoselReader
from machinery import ranking

def _prepare_mosel_data():
    mosel = MoselReader.do_magic()
    if mosel['code'] != 0:
        return mosel
    data = {}
    data['code']        = mosel['code']
    data['water_temp']  = str(int(mosel['temp'])) + "°"
    data['hoehe']       = mosel['hoehe']
    data['truebung']    = mosel['truebung']
    return data

def _prepare_weather_data():
    weather = WeatherReader.do_magic()
    if weather['code'] != 0:
        return weather
    data = {}
    data['code']        = weather['code']
    data['air_temp']    = str(int(weather['temp'])) + "°"
    data['icon']        = weather['icon']
    data['description'] = weather['description']
    data['sunset']      = weather['sunset']
    data['clouds']      = str(weather['clouds']) + " %"
    data['wind']        = str(int(weather['wind'] * 3.6)) + " km/h"
    data['humidity']    = str(weather['humidity']) + " %"
    return data

@app.route('/')
def index():
    mosel = _prepare_mosel_data()
    weather = _prepare_weather_data()
    print(weather)
    return render_template('HomePage.html', mosel=mosel, weather=weather)

@app.route('/about')
def measurement():
    return render_template('AboutPage.html')

@app.route('/ajax')
def ajax():
    return "Hello World!"

@app.route('/ranktab')
def rankt():
    rank_table = ranking.get_ranking_html()
    return rank_table

@app.route('/post', methods=['POST', 'GET'])
def post():
    username = request.args.get('name')
    result = {}

    if not username: #given string is empty
        result['code'] = 1
        result['msg'] = 'Kein Name angegeben.'
        result['title'] = "So geht's nicht."
        return jsonify(result)

    score, msg = ranking.insert_ranking(username)
    if score < 0:
        result['code'] = -1
        result['msg'] = msg
        result['title'] = 'Error.'
        return jsonify(result)

    result['code'] = 0
    result['msg'] = 'Du hast '+ str(score) +' Punkte für den Badegang erhalten.'
    result['title'] = 'Glückwunsch, ' + username + "!"
    return jsonify(result)
