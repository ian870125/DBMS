from flask import Flask, render_template,request,redirect,url_for, flash
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
                msg = "Member successfully Added" 
        except:  
            con.rollback()  
            msg = "We can not add the employee to the list" 
        finally:  
            return render_template("success.html",msg = msg)  
            con.close()
        
        
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
            msg = "Successfully login"
        else:
            flash('登入失敗了...')
    return redirect('/login')
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
    rows = cur.fetchall()
    return render_template("view2.html",rows = rows)

#系列賽比賽資訊網頁
@app.route("/view3")
def view3():
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("Select * from series  ") 
    t = cur.execute("Select") 
    rows = cur.fetchall()
      
    return render_template("view2.html",rows = rows)

    
@app.route("/money_add")
def money_add():
    return render_template("money_add.html")
 

 
    
if __name__ == '__main__':
   app.run(debug = True)