import os
from datetime import datetime, timedelta
from hashlib import sha256
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, request, session
from pymongo import MongoClient
load_dotenv(find_dotenv())


password = os.environ.get("MONGODB_PWD")
MONGODB_URI = f"mongodb+srv://admin:{password}@personalprojects.enxjsep.mongodb.net/"
client = MongoClient(MONGODB_URI)
database = client.FacialRecognitionWebApp

db_users = database.users

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def index():  
    user_is_logged_in = session.get('username') is not None
    username = session.get('username')

    return render_template("app/index.html", user_is_logged_in=user_is_logged_in, username=username)

@app.route("/register", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    repeat_password = request.form.get("repeat_password")

    if db_users.find_one({"username": username}):
        return render_template("auth/register.html", error="Username already exist. Please choose another username.", username=username, password=password, repeat_password=repeat_password)

    if password != repeat_password:
        return render_template("auth/register.html", error="Passwords do not match. Please try again.", username=username, password=password, repeat_password=repeat_password)

    db_users.insert_one({"username": username, "password": sha256(password.encode()).hexdigest()})

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def sign_in():
    if request.method == "GET":
        return render_template("auth/login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    passwordhash = sha256(password.encode()).hexdigest()

    user_doc = db_users.find_one({"username": username})

    if user_doc is None or user_doc["password"] != passwordhash:
        return render_template("auth/login.html", error="Wrong username or password. Try again or click \"Forgot your password?\" to reset it.")

    session["username"] = username

    session["is_admin"] = user_doc.get("is_admin", False)

    return redirect("/")

@app.route("/sign_out")
def sign_out():
    if "username" in session:
        session.pop("username")
    if "admin" in session:
        session.pop("admin")

    return redirect("/")


app.run("0.0.0.0", port=80, debug=True)