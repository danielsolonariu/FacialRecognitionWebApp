import os
from datetime import datetime
from hashlib import sha256

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session
from pymongo import MongoClient
from utils import get_data_uri, image_convert_BGR_to_RGB, compare_2_faces, change_date_format

load_dotenv(find_dotenv())


password = os.environ.get("MONGODB_PWD")
MONGODB_URI = f"mongodb+srv://admin:{password}@personalprojects.enxjsep.mongodb.net/"
client = MongoClient(MONGODB_URI)
database = client.FacialRecognitionWebApp

db_users = database.users
db_images = database.images

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

    return redirect("/login")

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

@app.route("/comparefaces", methods=["GET", "POST"])
def compare_faces():
    user_is_logged_in = session.get('username') is not None
    username = session.get('username')

    if request.method == "GET":
        return render_template("app/compare_faces.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               display_result=False)
    
    if request.method == "POST":
        allowed_extensions = ["png", "jpg", "jpeg", "bmp", "webp"]

        file_name_img1 = request.files["file1"].filename
        file_name_img2 = request.files["file2"].filename

        extension_img1 = file_name_img1.rsplit('.')[-1]
        extension_img2 = file_name_img2.rsplit('.')[-1]

        error_extension_message2 = "Please choose one of the following formats: [png, jpg, jpeg, bmp, webp]"

        if extension_img1 not in allowed_extensions and extension_img2 not in allowed_extensions:
            error_extension = True
            error_extension_message1 = "Both images do not have valid formats."
            return render_template("app/compare_faces.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               display_result=False,
                               error_extension=error_extension,
                               error_extension_message1=error_extension_message1,
                               error_extension_message2=error_extension_message2)

        elif extension_img1 not in allowed_extensions:
            error_extension = True
            error_extension_message1 = "The first image does not have a valid format."
            
            return render_template("app/compare_faces.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               display_result=False,
                               error_extension=error_extension,
                               error_extension_message1=error_extension_message1,
                               error_extension_message2=error_extension_message2)
        elif extension_img2 not in allowed_extensions:
            error_extension = True
            error_extension_message1 = "The second image does not have a valid format."
            return render_template("app/compare_faces.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               display_result=False,
                               error_extension=error_extension,
                               error_extension_message1=error_extension_message1,
                               error_extension_message2=error_extension_message2)

        date = datetime.now()
        insert_date = change_date_format(str(date))
        
        # Receive and manipulate images from users
        # file_name_img1 = request.files["file1"].filename
        file_data_img1 = request.files["file1"].stream.read()
        file_name_sha_img1 = sha256(file_data_img1).hexdigest()
        rgb_img1 = image_convert_BGR_to_RGB(file_data_img1)

        # file_name_img2 = request.files["file2"].filename
        file_data_img2 = request.files["file2"].stream.read()
        file_name_sha_img2 = sha256(file_data_img2).hexdigest()
        rgb_img2 = image_convert_BGR_to_RGB(file_data_img2)

        # Convert the binary image data to data URIs - to be used to display the images
        uri_img1 = get_data_uri(file_data_img1)
        uri_img2 = get_data_uri(file_data_img2)

        # Compare faces result
        result = bool(compare_2_faces(rgb_img1, rgb_img2)[0])

        if result == True:
            result_message = "SAME PERSON"
        else:
            result_message = "NOT THE SAME PERSON"

        # Insert data in the DB, only if there is an user logged in - to be used for history
        if user_is_logged_in:
            db_images.insert_one({
                "insert_date": insert_date,
                "user": username,
                "name_img1": file_name_img1,
                "sha256_img1": file_name_sha_img1,
                "data_img1": file_data_img1,
                "name_img2": file_name_img2,
                "sha256_img2": file_name_sha_img2,
                "data_img2": file_data_img2,
                "result": result,
            })

        return render_template("app/compare_faces.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               uri_img1=uri_img1,
                               uri_img2=uri_img2,
                               display_result=True,
                               result=result,
                               result_message=result_message)

@app.route("/comparefaces/history", methods=["GET", "POST"])
def compare_faces_history():
    if not session.get("username"):
        return redirect("/")
    
    user_is_logged_in = session.get('username') is not None
    username = session.get('username')

    records = [record for record in db_images.find({"user": username})]

    record_counter = 1
    for record in records:
        # Convert the binary image data to data URIs - to be used to display the images
        file_data_img1 = record["data_img1"]
        record["data_img1"] = get_data_uri(file_data_img1)
        file_data_img2 = record["data_img2"]
        record["data_img2"] = get_data_uri(file_data_img2)
        
        # Add counter value to each record
        record["counter"] = record_counter
        record_counter += 1


    if request.method == "GET":
        return render_template("app/compare_faces_history.html",
                               user_is_logged_in=user_is_logged_in,
                               username=username,
                               records=records)





app.run("0.0.0.0", port=80, debug=True)