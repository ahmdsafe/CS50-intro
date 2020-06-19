import os
import sqlite3
import re
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    USER_ID = session.get("user_id")
    con = sqlite3.connect('finance.db')
    cu = con.cursor()
    cu.execute("SELECT user_id, symbol, name, shares, price, total FROM stock WHERE user_id = :user_id AND NOT shares = 0",{'user_id': USER_ID})
    DATA = cu.fetchall()

    with con:
        cu.execute("SELECT SUM(total) FROM stock WHERE user_id = :user_id",{'user_id': USER_ID})
    SUM = cu.fetchone()
    if not SUM:
        SUM = 0.00

    rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=USER_ID)
    CASH = float(rows[0]["cash"])
    con.close()
    return render_template("index.html", CASH=CASH, DATA=DATA, SUM=SUM)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        if not request.form.get("symbol"):
            return apology("must provide symbol.", 403)

        elif not lookup(request.form.get("symbol")):
            return apology("invalid symbol!", 403)

        elif not request.form.get("shares"):
            return apology("must provide number of shares!", 403)

        elif int(request.form.get("shares")) < 1 :
            return apology("must provide positive number of shares!", 403)

        #starting a connection via sqlite3 normal way because cs50 way has no fetch function
        con = sqlite3.connect('finance.db')
        cu = con.cursor()

        #intiating variables with the user transaction data to be used later
        USER_ID = session.get("user_id")
        SYMBOL = request.form.get("symbol")
        SHARES = float(request.form.get("shares"))
        lookedUp = lookup(SYMBOL)
        NAME = lookedUp["name"]
        PRICE = float(lookedUp["price"])
        TOTAL = float(PRICE * SHARES)

        now = datetime.now()
        DATE = now.strftime("%d/%m/%Y %H:%M:%S")

        row = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=USER_ID)
        CASH = float(row[0]["cash"])
        CASH = float(CASH - TOTAL)
        if TOTAL > CASH:
            return apology("you don't have enough cash, you can add more from account menu", 403)
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", user_id = USER_ID, cash = CASH)
        db.execute("INSERT INTO history (User_id, Symbol, Shares, Price, time) VALUES (:user_id, :symbol, :shares, :price, :time)",
                        user_id=USER_ID, symbol=SYMBOL, shares=SHARES, price = PRICE, time=DATE)
        #check to see if the user has bought shares of that symbol before
        rows = db.execute("SELECT shares FROM stock WHERE symbol = :symbol AND user_id = :user_id",
                          symbol=SYMBOL, user_id = USER_ID)
        # if he bought shares of that company before we should add the shares he want to buy to the ones he already bought & update total
        if len(rows) > 0:
            with con:
                cu.execute("SELECT shares FROM stock WHERE symbol = :symbol AND user_id = :user_id",{'symbol': SYMBOL, 'user_id': USER_ID})
            shares_old = cu.fetchone()
            shares_old = float(shares_old[0])
            with con:
                cu.execute("SELECT total FROM stock WHERE symbol = :symbol AND user_id = :user_id",{'symbol': SYMBOL, 'user_id': USER_ID})
            total_old = cu.fetchone()
            total_old = float(total_old[0])

            con.close()
            db.execute("UPDATE stock SET shares = :shares, price = :price, total = :total WHERE symbol = :symbol AND user_id = :user_id",
                        symbol= SYMBOL, user_id = USER_ID, shares= SHARES + shares_old, price = PRICE, total = TOTAL + total_old)
        # if this the first time we just insert the data of his transaction to our stock table
        else:
            con.close()
            db.execute("INSERT INTO stock (user_id, symbol, name, shares, price, total) VALUES (:user_id, :symbol, :name, :shares, :price, :total)",
                        user_id=USER_ID, symbol=SYMBOL, name=NAME, shares=SHARES, price = PRICE, total=TOTAL)

        flash("Bought!")
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    USER_ID = session.get("user_id")
    con = sqlite3.connect('finance.db')
    cu = con.cursor()
    cu.execute("SELECT Symbol, Shares, Price, Time FROM history WHERE user_id = :user_id",{'user_id': USER_ID})
    DATA = cu.fetchall()
    con.close()
    return render_template("history.html", DATA=DATA)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        quoted = lookup(request.form.get("symbol"))
        if not quoted:
            return apology("invalid symbol!", 403)
        return render_template("quoted.html", quoted=quoted)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        PASSWORD = request.form.get("password")

        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords doesn't match", 403)

        elif len(request.form.get("password")) < 8 or not re.search("\d", PASSWORD) or not re.search("[a-z]", PASSWORD) or not re.search("[A-Z]", PASSWORD) or re.search("\s", PASSWORD):
            return apology("password is too week", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # check if username already exists
        if len(rows) == 1:
            return apology("username is taken, please choose another username", 403)

        USERNAME = request.form.get("username")
        HASH = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username=USERNAME, password=HASH)
        return redirect("/login")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        USER_ID = session.get("user_id")
        #starting a connection via sqlite3 normal way because cs50 way has no fetch function
        con = sqlite3.connect('finance.db')
        cu = con.cursor()
        with con:
            cu.execute("SELECT symbol FROM stock WHERE user_id = :user_id AND NOT shares = 0",{'user_id': USER_ID})
        SYMBOLS = cu.fetchall()
        con.close()
        return render_template("sell.html", SYMBOLS=SYMBOLS)

    else:
        if request.form.get("symbol") == "symbol":
            return apology("must provide a symbol!", 403)

        elif not request.form.get("shares"):
            return apology("must provide number of shares!", 403)

        elif int(request.form.get("shares")) < 1 :
            return apology("must provide positive number of shares!", 403)

        #starting a connection via sqlite3 normal way because cs50 way has no fetch function
        con = sqlite3.connect('finance.db')
        cu = con.cursor()

        #intiating variables with the user transaction data to be used later
        USER_ID = session.get("user_id")
        SYMBOL = request.form.get("symbol")
        SHARES = float(request.form.get("shares"))
        lookedUp = lookup(SYMBOL)
        PRICE = float(lookedUp["price"])
        TOTAL = float(PRICE * SHARES)

        with con:
            cu.execute("SELECT shares FROM stock WHERE user_id = :user_id AND symbol = :symbol",{'user_id': USER_ID, 'symbol': SYMBOL})
        shares=cu.fetchone()
        shares= float(shares[0])
        with con:
            cu.execute("SELECT total FROM stock WHERE user_id = :user_id AND symbol = :symbol",{'user_id': USER_ID, 'symbol': SYMBOL})
        total=cu.fetchone()
        total= float(total[0])
        if shares < SHARES:
            return apology("you don't have sufficient amount of shares", 403)

        db.execute("UPDATE stock SET shares = :shares, total = :total WHERE user_id = :user_id AND symbol = :symbol",
                    user_id = USER_ID, symbol = SYMBOL, shares = shares - SHARES, total = total - TOTAL)
        with con:
            cu.execute("SELECT cash FROM users WHERE id = :user_id",{'user_id': USER_ID})
        CASH=cu.fetchone()
        CASH= float(CASH[0])
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", user_id = USER_ID, cash = CASH + TOTAL)
        SHARES = SHARES * -1
        now = datetime.now()
        DATE = now.strftime("%d/%m/%Y %H:%M:%S")
        db.execute("INSERT INTO history (User_id, Symbol, Shares, Price, time) VALUES (:user_id, :symbol, :shares, :price, :time)",
                        user_id=USER_ID, symbol=SYMBOL, shares= SHARES, price = PRICE, time=DATE)

        con.close()
        flash("Sold!")
        return redirect("/")

@app.route("/account")
@login_required
def account():
    USER_ID = session.get("user_id")
    #starting a connection via sqlite3 normal way because cs50 way has no fetch function
    con = sqlite3.connect('finance.db')
    cu = con.cursor()
    with con:
            cu.execute("SELECT username FROM users WHERE id = :user_id",{'user_id': USER_ID})
    USERNAME = cu.fetchone()
    USERNAME = USERNAME[0]

    with con:
            cu.execute("SELECT cash FROM users WHERE id = :user_id",{'user_id': USER_ID})
    CASH = cu.fetchone()
    CASH = float(CASH[0])

    with con:
            cu.execute("SELECT COUNT(id) FROM history WHERE User_id = :user_id",{'user_id': USER_ID})
    TRANSACTIONS = cu.fetchone()
    TRANSACTIONS = TRANSACTIONS[0]

    with con:
            cu.execute("SELECT SUM(total) FROM stock WHERE User_id = :user_id",{'user_id': USER_ID})
    SUM = cu.fetchone()
    SUM = float(SUM[0]) + CASH
    PROFIT = SUM - 10000.00
    con.close()

    return render_template("account.html", USERNAME=USERNAME, CASH=CASH, TRANSACTIONS=TRANSACTIONS, PROFIT=PROFIT)

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "GET":
        return render_template("password.html")
    if request.method == "POST":
        USER_ID = session.get("user_id")
        # Ensure username was submitted
        if not request.form.get("password-old"):
            return apology("must provide old password", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide new password", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("new passwords doesn't match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=USER_ID)

        # Ensure password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password-old")):
            return apology("invalid old password!", 403)

        else:
            HASH = generate_password_hash(request.form.get("password"))

        db.execute("UPDATE users SET hash =:hash WHERE id = :user_id", user_id = USER_ID, hash = HASH)
        session.clear()

        # Redirect user to login form
        return redirect("/")

@app.route("/addCash", methods=["GET", "POST"])
@login_required
def addCash():
    if request.method == "GET":
        return render_template("addCash.html")
    if request.method == "POST":
        USER_ID = session.get("user_id")
        ADD= float(request.form.get("cash"))
        CREDIT = request.form.get("credit_no")
        LENGTH= len(CREDIT)
        SELECT = request.form.get("credit")
        if not ADD:
            return apology("must provide username", 403)

        elif ADD < 1:
            return apology("must provide number of dollars to add", 403)

        elif not CREDIT:
            return apology("must provide credit card number", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif SELECT == "Credit Card":
            return apology("must choose credit card type", 403)

        rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=USER_ID)
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid password!", 403)

        if SELECT == "AMEX" and LENGTH != 15:
            return apology("invalid credit card number", 403)
        if SELECT == "MASTERCARD" and LENGTH != 16:
            return apology("invalid credit card number", 403)
        if SELECT == "VISA" :
            if LENGTH != 16 and LENGTH != 13:
                return apology("invalid credit card number", 403)

        db.execute("UPDATE users SET cash =:cash WHERE id = :user_id", user_id = USER_ID, cash = float(rows[0]["cash"]) + ADD)
        return redirect("/")

@app.route("/symbols")
@login_required
def symbols():
    return render_template("symbols.html")

@app.route("/test")
def test():
    return render_template("test.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
