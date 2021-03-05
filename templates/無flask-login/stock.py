from flask import Flask
from flask import render_template #need to add floder "templates",
                                  #需和該py檔同層
from flask import url_for, redirect
from flask import request, session
from datetime import timedelta
import pandas as pd
from urllib.request import urlopen
import json
import requests
import pandas as pd
import time 
import flask_login

def stock_crawl(targets):
    timestamp = int(time.time() * 1000 + 1000000)
    stock_list = '|'.join('tse_{}.tw'.format(target) for target in targets)
    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?"+ stock_list
    query_url = '{}?_={}&ex_ch={}'.format(query_url, timestamp, stock_list)
    #print(query_url)
    try:
        data = json.loads(urlopen(query_url).read())
        column = ['c','n','z','tv','v','o','h','l','y']
        df = pd.DataFrame(data['msgArray'], columns=column)
        df.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量',
                     '累積成交量','開盤價','最高價','最低價','昨收價']
        df.insert(9, "漲跌百分比", 0.0)
        for x in range(len(df.index)):
            if df['當盤成交價'].iloc[x] != '-':
                df.iloc[x,[2,3,4,5,6,7,8]] = df.iloc[x,[2,3,4,5,6,7,8]].astype(float)
                df['漲跌百分比'].iloc[x] = (df['當盤成交價'].iloc[x]-df['昨收價'].iloc[x]) / df['昨收價'].iloc[x] * 100
    except:
        print('International Error, check you connection.')
    
    return df

app = Flask(__name__) #創建一個Flask的 instance
app.secret_key = '123456789'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(userMixin):
    pass

@login_manager.user_loader
def user_loader(account):
    with open('./member.json', 'r') as file:
        users = json.load(file)
    if account not in users:
        return
    user = User()
    user.id = account
    return user
    
@app.route('/', methods=['POST','GET'])
def index():
    if current_user.is_authenticated:
        with open('./member.json', 'r') as file:
            users = json.load(file)
        return render_template('test.html',
                                login=current_user.is_authenticated
                                username=user[current_user.id]['nick'])
    else:
        return render_template('test.html',
                                login=current_user.is_authenticated)

@app.route('/register', methods=['POST','GET'])
def Register():
    print("11111111111111")
    with open('./member.json','r') as file_object:
        print("2222")
        member = json.load(file_object)
    print("33333333333333")
    if request.method=='POST':
        print("4")
        if request.values['send']=='送出':
            if request.values['userid'] in member:
                for i in member:
                    if member[i]['nick']==request.values['username']:
                        return render_template('register.html',
                                            alert='This account and nickname is used')
                return render_template('register.html', 
                                alert='This account is used',
                                #把值留著?????????
                                nickname=request.values['username'])
            else:
                for i in member:
                    if member[i]['nick']==request.values['username']:
                        return render_template('register.html',
                                    alert='This nickname is used',
                                    id=request.values['userid'],
                                    pw=request.values['userpw'])
                print("5")
                member[request.values['userid']]={'password':request.values['userpw'],
                                                'nick':request.values['username']}
                with open('./member.json', 'w') as f:
                    json.dump(member, f)
                    print("123456789")
                return render_template('test.html')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def Login():
    if request.method=='POST':
        with open('./member.json','r') as file_obj:
            member = json.load(file_obj)
        if request.values['userid'] in member:
            if member[request.values['userid']]['password']==request.values['userpw']:
                user=request.values['userid']
                return render_template('test.html',user=user,USERS=USERS)
            else:
                return render_template('login.html',alert='Your password is wrong.')
        else:
            return render_template('login.html',alert='Your account is unregistered.')

    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def Logout():
    if request.method=='POST':
        if request.values['send']=='確定':
            user = None
            return redirect(url_for('index'))
        else:
            return render_template('test.html',user=user,USERS=USERS)
    return render_template('logout.html')

@app.route('/album')
def account():
    trans = pd.read_csv('./stock_trans.csv', dtype={'股票代號':str})
    trans = trans.loc[:,'買/賣':'損益']
    deposit = dict() #庫存
    price = dict() #庫存的單位平均成本
    diff = dict() #價差(含手續費，不含賣出手續費+交易稅)
    earn = 0
    for i in range(len(trans)): 
        name = trans['股票代號'].iloc[i]
        if name not in deposit:   
            if trans['買/賣'].iloc[i] == '買':
                deposit[name] = trans['股數'].iloc[i]
            else:
                deposit[name] = -trans['股數'].iloc[i]
            price[name] = trans['單位成本'].iloc[i]
            diff[name] = trans['淨收付'].iloc[i]
        else:
            p = deposit[name] / (trans['股數'].iloc[i] + deposit[name])
            price[name] = price[name] * p + trans['單位成本'].iloc[i] * (1-p)
            diff[name] += trans['淨收付'].iloc[i]
            if trans['買/賣'].iloc[i] == '買':
                deposit[name] += trans['股數'].iloc[i]
            else:
                deposit[name] -= trans['股數'].iloc[i]
                
        for k in list(deposit.keys()): #將庫存為0的刪掉
            if deposit[k] ==0:
                earn += diff[k]
                del diff[k]
                del deposit[k]
                del price[k]
    stock_list = list(deposit.keys())
    df = stock_crawl(stock_list)
    profit = dict() #當前損益(不含賣出交易稅&手續費)
    for name,now,cost,num in zip(deposit.keys(), df['昨收價'], diff.values(), deposit.values()):
        profit[name] = cost + now*num 
    return render_template('update.html', trans_record=deposit, profit=profit,
                            earn=earn)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5001", debug=True)

