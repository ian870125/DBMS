from flask import Flask, render_template,request,redirect
import sqlite3 
import hashlib
app = Flask(__name__)
 
con = sqlite3.connect("Gamble.db")  
#print("Database opened successfully")  
#con.execute("create table Employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, address TEXT NOT NULL)")  
#print("Table created successfully")  
 
@app.route("/")  
def index():  
    return render_template("index.html"); 
@app.route("/add")  
def add():  
    return render_template("add.html")  
  
@app.route("/savedetails",methods = ["POST"])  
def saveDetails():   
    if request.method == "POST":  
        try:  
            memberId = request.form["memberId"]  
            password = request.form["password"]  
            birthday = request.form["birthday"] 
            email = request.form["email"]
            accounts = request.form["accounts"]
            with sqlite3.connect("Gamble.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into  Member_info(memberId,password,birthday,accounts,email) values (?,?,?,?,?)",(memberId,password,birthday,accounts,email))  
                con.commit()  
                msg = "Member successfully Added" 
        except:  
            con.rollback()  
            msg = "We can not add the employee to the list" 
        finally:  
            return render_template("success.html",msg = msg)  
            con.close()
            

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
            return render_template("success.html",msg=msg)
        else:
            msg = "wrong ID"
    return redirect('/login')
    con.close()
 
@app.route("/view")  
def view():  
    con = sqlite3.connect("Gamble.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from Member_info")  
    rows = cur.fetchall()  
    return render_template("view.html",rows = rows)

@app.route("/login")
def login():
    return render_template("login.html")
    
@app.route("/money_add")
def money_add():
    return render_template("money_add.html")
 
@app.route("/delete")  
def delete():  
    return render_template("delete.html")  
 
@app.route("/deleterecord",methods = ["POST"])  
def deleterecord():  
    id = request.form["id"]  
    with sqlite3.connect("Gamble.db") as con:  
        try:  
            cur = con.cursor()  
            cur.execute("delete from Member_info where id = ?",id)  
            msg = "record successfully deleted" 
        except:  
            msg = "can't be deleted" 
        finally:  
            return render_template("delete_record.html",msg = msg)
 
    
if __name__ == '__main__':
   app.run(debug = True)