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

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

@app.route("/index")
def home():
    return render_template("app/index.html")



app.run("0.0.0.0", port=80, debug=True)