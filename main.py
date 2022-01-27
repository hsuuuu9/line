from flask import Flask, render_template, request, redirect, url_for
import tweepy
import random
import copy
import re
import openpyxl
from flask import Flask, request, Response, abort, render_template,session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
from sqlalchemy import create_engine
from requests_oauthlib import OAuth1Session
import pandas as pd
import pymysql
import datetime
import paramiko
from urllib.parse import urlparse,parse_qsl

pymysql.install_as_MySQLdb()
db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
url_sql = urlparse(db_path)
conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
pre_list = ['北海道',
'青森県',
'岩手県',
'宮城県',
'秋田県',
'山形県',
'福島県',
'茨城県',
'栃木県',
'群馬県',
'埼玉県',
'千葉県',
'東京都',
'神奈川県',
'新潟県',
'富山県',
'石川県',
'福井県',
'山梨県',
'長野県',
'岐阜県',
'静岡県',
'愛知県',
'三重県',
'滋賀県',
'京都府',
'大阪府',
'兵庫県',
'奈良県',
'和歌山県',
'鳥取県',
'島根県',
'岡山県',
'広島県',
'山口県',
'徳島県',
'香川県',
'愛媛県',
'高知県',
'福岡県',
'佐賀県',
'長崎県',
'熊本県',
'大分県',
'宮崎県',
'鹿児島県',
'沖縄県']
class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password
users = {}
letter = 'select * from user_list'
df = pd.read_sql(letter, conn)
for i in range(len(df)):
    users[i+1] = User(i+1, df['userid'][i], df['password'][i])

nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))




app.config['SECRET_KEY'] = "shuichi"


@app.route("/")
def zero():

    return render_template('zero.html')



@app.route("/line")
def twitter():
    try:
        asdf = session['username']
    except:
        session['username'] = 'anonymous'
    myna = session['username']
    login_flag = 'T'
    if myna == 'anonymous':
        login_flag = 'F'
    else:
        pass
    return render_template('main.html',myna = myna,login_flag = login_flag)

@app.route('/line/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            session['username'] = request.form["username"]
            return render_template("login_success.html",myname = session['username'])
        else:
            return render_template("login_fail.html")
    else:
        return render_template("login.html")


@app.route('/line/logout')
@login_required
def logout():
    logout_user()
    session['username'] = 'anonymous'
    return render_template('logout.html')



@app.route("/line/command")
@login_required
def command_get():
    user = session['username']

    return render_template('command.html',screen_name=user)


@app.route("/line/command/check")
@login_required
def check():
    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    length = len(df)
    ll = []
    for i in range(length):
        ll.append(df['japanese'][i])
    uu = []
    for i in range(length):
        uu.append(df['table_name'][i])

    return render_template('check.html',ll=ll,uu=uu,length = length)


@app.route("/line/command/check/<name>")
@login_required
def detail(name):
    letter = 'select * from '+name
    df = pd.read_sql(letter,conn)
    length = len(df)

    return render_template("variable.html", df=df,length = length)


@app.route("/line/command/collect", methods=["GET"])
def collect_get():
    user = session['username']

    return render_template('collect.html',user=user)

@app.route("/line/command/collect", methods=["POST"])
def collect_post():
    user = session['username']
    en = request.form.get("en")
    ja = request.form.get("ja")

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect('172.105.228.135', port=22, username='root', password='9&W(Ug?yCX=q')

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; sh /root/Desktop/line/matome.sh '+ja+' '+en+' ')


    return render_template('collect_result.html',stdout=stdout,stderr=stderr)

@app.route("/line/command/add", methods=["GET"])
def add_get():
    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    length = len(df)
    ll = []
    for i in range(length):
        ll.append(df['japanese'][i])


    return render_template('add.html',user=user,ll=ll,pp=pre_list)

@app.route("/line/command/add", methods=["POST"])
def add_post():
    user = session['username']
    job = request.form.get("job")
    place = request.form.get("place")
    friends1 = request.form.get("friends1")
    friends2 = request.form.get("friends2")
    user = 'shuichi'
    df_t = pd.read_sql('select * from tables where japanese = "'+job+'" ',conn)
    table = df_t['table_name'][0]
    letter = 'select * from '+table+' where prefecture = "'+place+'"'
    df = pd.read_sql(letter,conn)
    num = len(df)
    print('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/add.py '+table+' '+user+' '+place+' ')
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect('172.104.70.50', port=22, username='root', password='%WBcrc:m$&S{')

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/add.py '+table+' '+user+' '+place+' ')


    return render_template('add_result.html',job=job,place=place,num = num)


@app.route("/line/command/send", methods=["GET"])
def send_get():
    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    length = len(df)
    ll = []
    for i in range(length):
        ll.append(df['japanese'][i])


    return render_template('send.html',user=user,ll=ll,pp=pre_list)

@app.route("/line/command/send", methods=["POST"])
def send_post():
    user = session['username']
    job = request.form.get("job")
    place = request.form.get("place")
    user = 'shuichi'
    df_t = pd.read_sql('select * from tables where japanese = "'+job+'" ',conn)
    table = df_t['table_name'][0]
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect('172.104.70.50', port=22, username='root', password='%WBcrc:m$&S{')

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/send.py '+table+' '+user+' '+place+' ')


    return render_template('send_result.html',job=job,place=place)


if __name__ == '__main__':
    app.run(debug=True)
