from flask import Flask, render_template,request,redirect,url_for, flash,session
import sqlite3 
import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os



app = Flask(__name__)



totime = datetime.datetime.now() 
con = sqlite3.connect("Gamble.db")  
#print("Database opened successfully")  
#con.execute("create table Employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, address TEXT NOT NULL)")  
#print("Table created successfully")  

#會員登入的設定
app.secret_key = app.config.get('flask', 'yangyang')
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = '請證明你是豬逼'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def user_loader(userpig):
    user = User(userpig)
    return user

@login_manager.request_loader
def request_loader(userpig):
    user = User(userpig)
    return user

#首頁
@app.route("/")  
def index():  
    return render_template("index.html"); 

#加入會員網頁
@app.route("/add")  
def add():  
    return render_template("add.html")  


#加入會員後送出的動作
@app.route("/savedetails",methods = ["POST"])  
def saveDetails():   
    if request.method == "POST":  
        try:  
            memberId = request.form["memberId"]  
            password = request.form["password"]  
            birthday = request.form["birthday"] 
            identity = request.form["identity"]
            accounts = request.form["account"]
            with sqlite3.connect("Gamble.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into  member_info(memberId,password,birthday,identity,account) values (?,?,?,?,?)",(memberId,password,birthday,identity,accounts))  
                con.commit()  
                 
        except:  
            con.rollback()  
            flash("輸入有問題") 
        finally:  
            return render_template("success_add.html",user_id = memberId)  
            con.close()

#比賽資訊網頁
@app.route("/view")  
def view():  
    return render_template("view_index.html")
#單場比賽資訊網頁
@app.route("/view2")
def view2():
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()
    date = '2023-04-18'
    cur.execute("SELECT * FROM single_match WHERE date > DATE('2023-04-18') AND date = (SELECT date FROM single_match WHERE date > DATE('2023-04-18') Order By date asc);")  
    con.commit()
    rows = cur.fetchall()
    return render_template("view2.html",rows = rows)

#系列賽比賽資訊網頁
@app.route("/view3")
def view3():
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("Select * from series  ") 
    rows = cur.fetchall()
      
    return render_template("view2.html",rows = rows)
#NBA球隊資訊
@app.route("/team")
def team():
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("Select * from NBA_playoff_teams  ") 
    rows = cur.fetchall()
      
    return render_template("team.html",rows = rows)
@app.route("/player")
#NBA球員資訊
def player():
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("Select * from NBA_playoff_players  ") 
    rows = cur.fetchall()
      
    return render_template("player.html",rows = rows)
#登入網頁
@app.route("/login")
def login():
    return render_template("login.html")
#登戶會員後的動作
@app.route("/login_result",methods = ["POST"]) 
def login_Result():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()
        
    if  "memberId" in request.form and "password" in request.form:   
        memberId = request.form["memberId"]  
        password = request.form["password"]
            
        cur.execute("Select * From Member_info Where memberId = ? and password = ?",(memberId,password))
        result = cur.fetchone()
        if result:
            user = user_loader(memberId)
            login_user(user)
            return render_template("index_in.html",user_id=current_user.id)
        else:
            flash('登入失敗了...')
    return redirect('/login')
    con.close()

@app.route('/logout')
def logout():
    users = current_user.id
    logout_user()
    return render_template("logout.html",user = users)
    
    
    
#入金的網頁
@app.route("/money_in")
@login_required  
def money_in():
    user = current_user.id   
    return render_template("money_in.html",user =user )

@app.route("/money_add",methods=["POST"])
@login_required 
def money_add():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()
    money = int(request.form["money"])
    password = request.form["password"]
    cur.execute("UPDATE member_info SET money = money + ? WHERE password = ? ", (money,password))
    con.commit()
    return render_template("money_in_success.html",money = money , user = current_user.id)
    

 
    
if __name__ == '__main__':
   app.run(debug = True)