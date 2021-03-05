from flask import Flask
from flask import render_template #need to add floder "templates",
                                  #需和該py檔同層
from flask import url_for, redirect
from flask import request

app = Flask(__name__) #創建一個Flask的 instance
@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if request.values['send']=='送出': #按下送出的話，才執行下面的東西
            print(request.values['user'])
            return render_template('index.html',name=request.values['user'])
    return render_template('index.html', name="")

@app.route('/<int:userID>')
def hello(userID):
     return 'The user ID is: {}'.format(str(userID))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5001", debug=True)

'''
@app.route("/") #告訴你怎樣的url可以call怎樣的function
def test():
    return "Hello World!"
# 到瀏覽器輸入127.0.0.1:5001/(你的名字)
@app.route("/<name>")
def flask(name):
    return "Hello " + name + "!"

@app.route("/")
@app.route('/<name>')
def combine(name=None):
    if name == None :
        return "Hello World!"
    return "Hello " + name + "!"
'''
'''
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/second')
def second():
    # url_for 的回傳值試找到相同名稱 function 指向的路由(route)顯示出來
    # redirect 導向指向的路由
    return redirect(url_for('index'))
'''