from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///register.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    users = db.execute("SELECT * FROM registrants")
    return render_template("register.html", users=users)

@app.route("/new_register" , methods=["GET", "POST"])
def registerN():
    if request.method == "GET":
        return render_template("new_register.html")
    else:
        NAME = request.form.get("name")
        EMAIL = request.form.get("email")
        db.execute("INSERT INTO registrants (name, email) VALUES (:name, :email)", name=NAME, email=EMAIL)
        return redirect("/register")


@app.route("/sites")
def sites():
    return render_template("sites.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/tasks")
def tasks():
    if "todos" not in session:
        session["todos"] = []
    return render_template("tasks.html", todos=session["todos"])

@app.route("/new_task", methods=["GET", "POST"])
def taskN():
    if request.method == "GET":
        return render_template("new.html")
    else:
        todo = request.form.get("task")
        session["todos"].append(todo)
        return redirect("/tasks")

@app.route("/about")
def about():
    return render_template("about.html")
