from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import datetime
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import os

app = Flask(__name__)

totime = datetime.datetime.now()
con = sqlite3.connect("Gamble.db")
# print("Database opened successfully")
# con.execute("create table Employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, address TEXT NOT NULL)")
# print("Table created successfully")

# 會員登入的設定
app.secret_key = app.config.get("flask", "yangyang")
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = "請證明你是豬逼"


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


# 首頁
@app.route("/")
def index():
    return render_template("index.html")


# 加入會員網頁
@app.route("/add")
def add():
    return render_template("add.html")


# 加入會員後送出的動作
@app.route("/savedetails", methods=["POST"])
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
                cur.execute(
                    "INSERT into member_info(memberId,password,birthday,identity,account) values (?,?,?,?,?)",
                    (memberId, password, birthday, identity, accounts),
                )
                con.commit()

        except:
            con.rollback()
            flash("輸入有問題")
        finally:
            return render_template("success_add.html", user_id=memberId)
            con.close()


# 比賽資訊網頁
@app.route("/view")
def view():
    return render_template("view_index.html")


# 單場比賽資訊網頁
@app.route("/view2")
def view2():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    date = "2023-04-18"
    cur.execute(
        # "SELECT * FROM match_info WHERE date > DATE('2023-04-18') AND date = (SELECT date FROM single_match WHERE date > DATE('2023-04-18') Order By date asc);"
        "SELECT * FROM match_info WHERE `賽事種類` = '單場賽場' Order By date;"
    )
    con.commit()
    rows = cur.fetchall()
    return render_template("view2.html", rows=rows)


# 系列賽比賽資訊網頁
@app.route("/view3")
def view3():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from match_info WHERE `賽事種類` = '系列賽' Order By date")
    rows = cur.fetchall()

    return render_template("view2.html", rows=rows)


# NBA球隊資訊
@app.route("/team")
def team():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from NBA_playoff_teams  ")
    rows = cur.fetchall()

    return render_template("team.html", rows=rows)


# NBA球員資訊
@app.route("/player")
def player():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from NBA_playoff_players  ")
    rows = cur.fetchall()

    return render_template("player.html", rows=rows)


# 登入網頁
@app.route("/login")
def login():
    return render_template("login.html")


# 登戶會員後的動作
@app.route("/login_result", methods=["POST"])
def login_Result():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    if "memberId" in request.form and "password" in request.form:
        memberId = request.form["memberId"]
        password = request.form["password"]

        cur.execute(
            "Select * From Member_info Where memberId = ? and password = ?",
            (memberId, password),
        )
        result = cur.fetchone()
        if result:
            user = user_loader(memberId)
            login_user(user)
            return render_template("index_in.html", user_id=current_user.id)
        else:
            flash("登入失敗了...")
    return redirect("/login")
    con.close()


@app.route("/logout")
def logout():
    users = current_user.id
    logout_user()
    return render_template("logout.html", user=users)


# 出入金的網頁
@app.route("/money_in_out")
@login_required
def money_in_out():
    # 再次查詢更新後的 member_info
    user = current_user.id
    return render_template("money_in_out.html", user=user)


# 出入金成功的網頁
@app.route("/money_add", methods=["POST"])
@login_required
def money_add():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    action = request.form["action"]
    in_out_money = int(request.form["money"])
    password = request.form["password"]

    if action == "deposit":
        cur.execute(
            "UPDATE member_info SET money = money + ? WHERE password = ?",
            (in_out_money, password),
        )
        action_text = "儲值"
        in_out_text = "進入"
    elif action == "withdraw":
        cur.execute("SELECT money FROM member_info WHERE password = ?", (password,))
        current_money = cur.fetchone()[0]
        if current_money < in_out_money:
            error_message = "錯誤：提領金額超過帳戶餘額"
            return render_template(
                "money_in_out_error.html", error_message=error_message
            )

        cur.execute(
            "UPDATE member_info SET money = money - ? WHERE password = ?",
            (in_out_money, password),
        )
        action_text = "提領"
        in_out_text = "出"
    con.commit()

    # 再次查詢更新後的 member_info
    cur.execute("SELECT money FROM member_info WHERE password = ?", (password,))
    updated_money = cur.fetchone()[0]

    # 插入操作紀錄到 money_records 資料表中
    user_id = current_user.id
    cur.execute(
        "INSERT INTO money_records (user_id, action, amount) VALUES (?, ?, ?)",
        (user_id, action_text, in_out_money),
    )
    con.commit()

    return render_template(
        "money_in_out_success.html",
        money=in_out_money,
        user=current_user.id,
        action=action_text,
        in_out=in_out_text,
        updated_money=updated_money,  # 傳遞更新後的 money
    )


# 出入金紀錄
@app.route("/money_in_out_record")
@login_required
def money_in_out_record():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    user_id = current_user.id

    # 查詢 money_records 表格中屬於當前使用者的紀錄
    cur.execute(
        "SELECT action, amount, created_at FROM money_records WHERE user_id = ?",
        (user_id,),
    )
    records = cur.fetchall()

    return render_template("money_in_out_record.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)