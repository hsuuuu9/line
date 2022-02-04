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


@app.route("/line/command/check", methods=["GET"])
@login_required
def check_get():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    jp = []
    for i in range(len(df)):
        jp.append(df['japanese'][i])

    en = []
    for i in range(len(df)):
        en.append(df['table_name'][i])

    length = (len(df))

    return render_template('check.html',user=user,jp=jp,en=en,length = length,pp=pre_list)


@app.route("/line/command/check", methods=["POST"])
@login_required
def check_post():
    job = request.form.get("job")
    place = request.form.get("place")
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    df = pd.read_sql('select * from tables',conn)
    jap = df[df['table_name'] == job]['japanese'][df[df['table_name'] == job].index[0]]
    if not place == '全国':
        letter = 'select * from '+job+' where prefecture = "'+place+'" '
        df = pd.read_sql(letter,conn)
        length = len(df)
    else:
        letter = 'select * from '+job
        df = pd.read_sql(letter,conn)
        length = len(df)
    return render_template("check_result.html",length = length,jap=jap,place=place)


@app.route("/line/command/collect", methods=["GET"])
def collect_get():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    jp = []
    for i in range(len(df)):
        jp.append(df['japanese'][i])

    en = []
    for i in range(len(df)):
        en.append(df['table_name'][i])

    length = (len(df))

    return render_template('collect.html',user=user,jp=jp,en=en,length = length,pp=pre_list)

@app.route("/line/command/collect", methods=["POST"])
def collect_post():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    job = request.form.get("job")
    place = request.form.get("place")
    detail = request.form.get("detail")

    df = pd.read_sql('select * from tables',conn)
    jap = df[df['table_name'] == job]['japanese'][df[df['table_name'] == job].index[0]]

    letter = 'insert into premium values("'+jap+'","'+place+'","'+detail+'") '
    conn.execute(letter)

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect('172.105.230.158', port=22, username='root', password='NZAPK[+[dm:9')

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; sh /root/Desktop/okuru/matome-order.sh '+job+' '+place+' '+detail)


    return render_template('collect_result.html',stdout=stdout,stderr=stderr)

@app.route("/line/command/add", methods=["GET"])
def add_get():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

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
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    job = request.form.get("job")
    place = request.form.get("place")
    user = 'shuichi'
    df_user = pd.read_sql('select * from user_list where userid = "'+user+'"',conn)
    IP = df_user['SERVER_IP'][0]
    Password = df_user['SERVER_PASS'][0]
    df_t = pd.read_sql('select * from tables where japanese = "'+job+'" ',conn)
    table = df_t['table_name'][0]
    letter = 'select * from '+table+' where prefecture = "'+place+'"'
    df = pd.read_sql(letter,conn)
    num = len(df)
    print('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/add.py '+table+' '+user+' '+place+' ')
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(IP, port=22, username='root', password=Password)

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/add.py '+table+' '+user+' '+place+' ')


    return render_template('add_result.html',job=job,place=place,num = num)


@app.route("/line/command/send")
def send_get():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    letter = 'select * from stock where username = "'+user+'"'
    df = pd.read_sql(letter,conn)
    choice = []
    for i in range(len(df)):
        choice.append(df['tablename'][i])
    last = list(set(choice))

    df = pd.read_sql('select * from tables',conn)
    nn = []
    for la in last:
        jap = df[df['table_name'] == la]['japanese'][df[df['table_name'] == la].index[0]]
        nn.append(jap)
    length = len(df)


    return render_template('send.html',user=user,last=last,nn=nn,length=length)

@app.route("/line/command/send/<name>", methods=["GET"])
@login_required
def detail(name):
    user = session['username']
    letter = 'select distinct * from stock where username = "'+user+'" and tablename = "'+name+'" '
    print(letter)
    df = pd.read_sql(letter,conn)
    print(len(df))
    length = len(df)
    pl = []
    for i in range(length):
        pl.append(df['prefecture'][i])

    df_a = pd.read_sql('select * from '+name,conn)
    dic = {}
    for pre in pre_list:
        dic[pre] = len(df_a[df_a['prefecture'] == pre])

    df = pd.read_sql('select * from tables',conn)
    jap = df[df['table_name'] == name]['japanese'][df[df['table_name'] == name].index[0]]

    df = pd.read_sql('select * from messege where username = "'+user+'" and job = "'+name+'" ',conn)
    messege = []
    for i in range(len(df)):
        messege.append(df['messege'][i])

    length_m = len(messege)

    title = []
    for i in range(len(df)):
        title.append(df['title'][i])

    return render_template("variable.html", pl=pl,jap=jap,dic=dic,length=length,messege=messege,length_m=length_m,title=title)






@app.route("/line/command/send/<name>", methods=["POST"])
@login_required
def send_post(name):
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    job = name
    place = request.form.get("place")
    messege = request.form.get("messege")
    table = job
    df = pd.read_sql('select * from tables',conn)
    jap = df[df['table_name'] == job]['japanese'][df[df['table_name'] == job].index[0]]

    df_user = pd.read_sql('select * from user_list where userid = "'+user+'"',conn)
    IP = df_user['SERVER_IP'][0]
    Password = df_user['SERVER_PASS'][0]
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(IP, port=22, username='root', password=Password)

        # コマンド実行
        stdin, stdout, stderr = ssh.exec_command('export DISPLAY=:1.0 ; pkill chrome ; python3 /root/Desktop/line/send.py '+table+' '+user+' '+place+' '+'"'+messege+'"')


    return render_template('send_result.html',jap=jap,place=place)


@app.route("/line/command/make", methods=["GET"])
@login_required
def make():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    letter = 'select * from tables'
    df = pd.read_sql(letter,conn)
    jp = []
    for i in range(len(df)):
        jp.append(df['japanese'][i])

    en = []
    for i in range(len(df)):
        en.append(df['table_name'][i])

    length = (len(df))

    return render_template('make.html',user=user,jp=jp,length = length,en=en)


@app.route("/line/command/make", methods=["POST"])
@login_required
def make_post():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    job = request.form.get("job")
    title = request.form.get("title")
    messege = request.form.get("messege")
    letter = 'insert into messege values("'+user+'","'+job+'","'+title+'","'+messege+'") '
    conn.execute(letter)


    m = messege.split('\n')
    length = len(m)

    return render_template('make_result.html',m=m,job=job,length=length,title=title,user=user)

@app.route("/line/command/delete", methods=["GET"])
@login_required
def edit():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']

    df = pd.read_sql('select * from messege where username = "'+user+'" ',conn)
    messege = []
    for i in range(len(df)):
        messege.append(df['messege'][i])

    length_m = len(messege)

    title = []
    for i in range(len(df)):
        title.append(df['title'][i])

    length_m = len(title)


    return render_template('delete.html',title=title,messege=messege,length_m=length_m)

@app.route("/line/command/delete", methods=["POST"])
@login_required
def edit_post():
    pymysql.install_as_MySQLdb()
    db_path = "mysql://shuichi47:V3BtyW&U@172.104.91.29:3306/Line"
    url_sql = urlparse(db_path)
    conn = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(host = url_sql.hostname, port=url_sql.port, user = url_sql.username, password= url_sql.password, database = url_sql.path[1:]))

    user = session['username']
    title = request.form.get("title")
    letter = 'delete from messege where username = "'+user+'" and title = "'+title+'" '
    conn.execute(letter)


    return render_template('delete_result.html',title=title)


if __name__ == '__main__':
    app.run(debug=True)
