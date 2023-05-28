import re
import os
import shutil
import logging
import datetime
import traceback
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from ntplib import NTPClient, NTPException
from datetime import timezone
from datetime import datetime as dt
from multiprocessing import Process
import multiprocessing_logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, render_template, request, make_response, send_file, jsonify, json, redirect, url_for, session

path = Path.cwd()  
web_port = int(os.environ['WEBSERVER_PORT'])
web_host = os.environ['WEBSERVER_HOST']
logs = path.joinpath(os.environ['PATHS_LOGS'])
database = path / 'database'
models = path / 'models'
utils = path / 'utils'

app = Flask(__name__)

# ГЛАВНАЯ СТРАНИЦА ИНДЕКС WEB
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route('/index')
def index():
    return render_template('index.html'), 200
    

# ПРОВЕРКА ПОДКЛЮЧЕНИЯ JSON
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route("/")
def welcome():
    return render_template('index.html'), 200
    #return jsonify( message='Welcome to Recommendation platform'), 200


# СТРАНИЦА РЕКОМЕНДАЦИЙ
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route('/recommendations', methods=['GET'])
def recommendations():
    if request.method == 'GET':
        message=json.dumps('Welcome to Recommendation platform'), 200
        title='В ближайшее время'
        data='Туса на марсе'
    return render_template("recommendations.html", title=title, data=data)


# ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ JSON
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route('/info', methods=['GET'])
def info():
    return jsonify(
        branch=os.environ['BRANCH'],
        build=os.environ['BUILD']), 200


# ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ WEB
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route('/about', methods=['GET'])
def about():
    if request.method == 'GET':
        branch=os.environ['BRANCH'], 200
        build=os.environ['BUILD'], 200
    return render_template("about.html", branch=branch, build=build)

# АУТЕНТИФИКАЦИЯ JSON
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.route('/auth', methods=['POST'])
def authorization():
    # проверка ключей запроса и ip адреса пользователя
    ip_address = request.remote_addr
    try:
        data = request.json
        full_name = str(data['fio'])
        date_of_birth = str(data['inputDate'])
        app.logger.info(f"Authorization attempt of user with full_name={full_name}, date_of_birth={date_of_birth}")
    except Exception as e:
        app.logger.error(f"Authorization attempt with incorrect request body: {e}, ip_address={ip_address}")
        return jsonify(session_token=None,
                       message="ERROR: POST request body is incorrect (JSON should contain full_name, date_of_birth)"), 400


@app.route("/auth_web")
def auth_web():
    return render_template('auth_web.html')




# странички с тестами
@app.route('/test/')
def test():
    return render_template('test.html')

@app.route('/test_dusha/')
def test_dusha():
    return render_template('test_dusha.html')

@app.route('/test_telo/')
def test_telo():
    return render_template('test_telo.html')

@app.route('/raion/')
def raion():
    return render_template('raion.html')

@app.route('/imt/')
def imt():
    return render_template('imt.html')

@app.route('/activity/')
def iactivitymt():
    return render_template('activity.html')

# ERROR HANDLERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
@app.errorhandler(400)
def api_400(error_message):
    return jsonify(
        error_message=str(error_message)
    ), 400


@app.errorhandler(401)
def api_401(error_message):
    return jsonify(
        error_message=str(error_message)
    ), 401


@app.errorhandler(404)
def api_404(error_message):
    return jsonify(
        error_message=str(error_message)
    ), 404


@app.errorhandler(405)
def api_405(error_message):
    return jsonify(
        error_message=str(error_message)
    ), 405


@app.errorhandler(500)
def api_500(error_message):
    return jsonify(
        error_message=str(error_message)
    ), 500

# ПОДГРУЗКА И СБОРКА ПРОЕКТА
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
if __name__ == '__main__':

        # проверка наличия директорий
    path_cfg = {
        'database': database,
        'models': models,
        'utils': utils,
        'logs': logs,
    }

    for key in path_cfg:
        try:
            Path(path_cfg[key]).mkdir(parents=False, exist_ok=False)
            print("Folder create")
        except:
            print("Folder exists")

    # настройка логирования
    handler = TimedRotatingFileHandler(os.path.join(logs, 'logs.log'), when='H', interval=1, backupCount=60)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.suffix = "%Y-%m-%d_%H-%M-%S"
    handler.extMatch = re.compile(r"^\d{8}$")
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    multiprocessing_logging.install_mp_handler()

    # запустить сервер
    app.run(
        debug=True, 
        host=web_host, 
        port=web_port, 
    )