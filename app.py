#!/usr/bin/env python3
from flask import (
    Flask,
    make_response,
    render_template,
    request,
    redirect,
    url_for,
    abort,
)
import sys
import ast
import json
import random

from crud import read, find_user, add_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from data_exploration import split_words

sys.stdout = open("out.txt", "w")

def create_app():
    app = Flask(__name__)
    #app.config["SECRET_KEY"] = "secretkey"
    app.dishes = list(read("food.db", "dishes"))
    app.username = ""
    app.tags = list(read("food.db", "tags"))
    app.display = {"thumbnail_url": "Image", "name": "Name of Recipe", "total_time": "Total Time"}
    app.flirts = []
    app.valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-"
    return app


app = create_app()

@app.route("/")
def home():
    return render_template("home.html", dishes=app.dishes, tags=app.tags, username=app.username)


@app.post("/")
def post_index():
    if request.form:
        fdata = dict(request.form)
        result = []
        
        keywords = split_words(fdata.get("keywords", "").lower())
        for dish in app.dishes:
            cond = True
            diet, cuisine = fdata.get("diet", dish["tags"]), fdata.get("cuisine", dish["tags"])
            for v in [diet, cuisine]:
                if not v in dish["tags"]:
                    cond = False
                    break
            dwords = (dish["name"] + dish["keywords"]).lower()
            for kword in keywords:
                if not kword in dwords:
                    cond = False
                    break
            if cond:
                result.append(dish)
        return render_template(
            "index.html", dishes=result, display=app.display
        )
    else:
        return render_template(
            "index.html", dishes=app.dishes, display=app.display
        )
        
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        if find_user("data.db", "admin", request.form["username"], request.form["password"]):
            app.username = request.form["username"]
            return render_template("home.html", username=app.username)
        else:
            error = "Invalid Credentials"
    return render_template('signin.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if not all(e in app.valid_chars for e in request.form["username"]):
            error = "Username can only contain " + app.valid_chars
        elif request.form["password"] != request.form["password_confirm"]:
            error = "Passwords don't match"
        elif not all(e in app.valid_chars for e in request.form["password"]):
            error = "Password can only contain " + app.valid_chars
        elif add_user("data.db", "admin", request.form['username'], request.form['password']):
            app.username = request.form["username"]
            return render_template("home.html", username=app.username)
        else:
            error = "Username already in use"
    return render_template('signup.html', error=error)

@app.route("/signout")
def signout():
    app.username = ""
    return render_template("home.html", username=app.username)
    
@app.route("/profile")
def profile():
    return render_template("profile.html", username=app.username)

@app.route("/<int:dish_id>")
def dish_by_id(dish_id):
    for dish in app.dishes:
        if dish["id_"] == dish_id:
            with open("archive/ingredient_and_instructions.json") as f:
                d = json.load(f)
            return render_template("details.html", dish=dish, ingredient=d[dish["slug"]])
    
    abort(404)


@app.route("/flirthome")
def flirt_home():
    return render_template("flirt_home.html")

@app.route("/flirt")
def flirt():
    rdish = app.dishes[random.randint(0, len(app.dishes))]
    return render_template("flirt.html", dish=rdish)

@app.post("/flirt")
def post_flirt():
    if (request.form):
        fdata = dict(request.form)
        action = fdata["action"]
        if (action == "quit"):
            dishes = app.flirts
            app.flirts = []
            return render_template("index.html", dishes=dishes, display=app.display)
        elif (action == "save"):
            ddish = ast.literal_eval(fdata["dish"])
            app.flirts.append(ddish)

        rdish = app.dishes[random.randint(0, len(app.dishes))]
        return render_template("flirt.html", dish=rdish)
        
    abort(404)

@app.route("/contact")
def load_contact():
    return render_template("contact.html")