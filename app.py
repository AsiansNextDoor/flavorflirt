 #!/usr/bin/env python3
from flask import (
    Flask,
    make_response,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    session,
)
import sys
import ast
import json
import random

from crud import read, find_user, verify_user, add_user, modify, read_list
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
    app.tags = list(read("food.db", "tags"))
    app.display = {"thumbnail_url": "Image", "name": "Name of Recipe", "total_time": "Total Time"}
    app.user = ["", False, []]
    app.valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-"
    return app


app = create_app()

app.secret_key = b"\x87c\xed\xda\x82\xf5\xcdF]\xa7N0L\x94b3"


@app.route("/")
def home():
    if session.get("username"):
        print(session["username"])
    return render_template("home.html", dishes=app.dishes, tags=app.tags, user=app.user)


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
            "index.html", dishes=result, display=app.display, user=app.user
        )
    else:
        return render_template(
            "index.html", dishes=app.dishes, display=app.display, user=app.user
        )
        
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        if verify_user("data.db", "users", request.form["username"], request.form["password"]):
            app.user[0] = request.form["username"]
            app.user[1] = False
            app.user[2] = read_list("recipes.db", "saved", request.form['username'])
            session["username"] = request.form["username"]
            session["ifadmin"] = False
            session["recipes"] = read_list("recipes.db", "saved", request.form['username'])
            return redirect(url_for("home"))
        elif verify_user("data.db", "admins", request.form["username"], request.form["password"]):
            app.user[0] = request.form["username"]
            app.user[1] = True
            app.user[2] = read_list("recipes.db", "saved", request.form['username'])
            session["username"] = request.form["username"]
            session["ifadmin"] = True
            session["recipes"] = read_list("recipes.db", "saved", request.form['username'])
            return redirect(url_for("home"))
        else:
            error = "Invalid Credentials"
    return render_template('signin.html', error=error, user=app.user)

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
        elif find_user("data.db", "users", request.form['username'], request.form['password']) or find_user("data.db", "admins", request.form['username'], request.form['password']):
            error = "Username already in use"
        else:
            add_user("data.db", "users", request.form['username'], request.form['password'])
            modify("recipes.db", "saved", request.form['username'], [])
            return redirect(url_for("home"))
    return render_template('signup.html', error=error, user=app.user)

@app.route('/adminsignup', methods=['GET', 'POST'])
def admin_signup():
    error = None
    if request.method == 'POST':
        if not all(e in app.valid_chars for e in request.form["username"]):
            error = "Username can only contain " + app.valid_chars
        elif request.form["password"] != request.form["password_confirm"]:
            error = "Passwords don't match"
        elif not all(e in app.valid_chars for e in request.form["password"]):
            error = "Password can only contain " + app.valid_chars
        elif find_user("data.db", "users", request.form['username'], request.form['password']) or find_user("data.db", "admins", request.form['username'], request.form['password']):
            error = "Username already in use"
        else:
            add_user("data.db", "admins", request.form['username'], request.form['password'])
            modify("recipes.db", "saved", request.form['username'], [])
            return redirect(url_for("home"))
    return render_template('admin_signup.html', error=error, user=app.user)

@app.route("/signout")
def signout():
    app.user[0] = ""
    app.user[1] = False
    app.user[2] = []
    session.pop('username', None)
    session.pop('ifadmin', None)
    session.pop('recipes', None)
    return render_template("home.html", dishes=app.dishes, tags=app.tags)
    
@app.route("/recipes")
def recipes():
    return render_template("recipes.html", display=app.display, user=app.user)

@app.post("/recipes")
def post_recipes():
    if not session.get("username"):
        return redirect(url_for("home"))
    if request.form:
        fdata = dict(request.form)
        dish = ast.literal_eval(fdata["dish"])
        saved_dishes = read_list("recipes.db", "saved", session["username"])
        if dish in saved_dishes:
            saved_dishes.remove(dish)
        session["recipes"] = saved_dishes
        modify("recipes.db", "saved", session["username"], saved_dishes)
        return render_template("recipes.html", display=app.display, user=app.user)
    abort(404)
        
        

@app.route("/<int:dish_id>")
def dish_by_id(dish_id):
    for dish in app.dishes:
        if dish["id_"] == dish_id:
            with open("archive/ingredient_and_instructions.json") as f:
                d = json.load(f)
            return render_template("details.html", dish=dish, ingredient=d[dish["slug"]], user=app.user)
    
    abort(404)


@app.route("/flirthome")
def flirt_home():
    return render_template("flirt_home.html", user=app.user)

@app.route("/flirt")
def flirt():
    rdish = app.dishes[random.randint(0, len(app.dishes))]
    return render_template("flirt.html", dish=rdish, user=app.user)

@app.post("/flirt")
def post_flirt():
    if not session.get("username"):
        return redirect(url_for("home"))
    if request.form:
        fdata = dict(request.form)
        action = fdata["action"]
        
        if action == "quit":
            return redirect(url_for("recipes"))
        elif action == "save" and session["username"]:
            dish = ast.literal_eval(fdata["dish"])
            saved_dishes = read_list("recipes.db", "saved", session["username"])
            if saved_dishes:
                saved_dishes.append(dish)
            else:
                saved_dishes = [dish]
            session["recipes"] = saved_dishes
            modify("recipes.db", "saved", session["username"], saved_dishes)
        
        rdish = app.dishes[random.randint(0, len(app.dishes) - 1)]
        return render_template("flirt.html", dish=rdish, user=app.user)
    
    abort(404)

@app.route("/contact")
def load_contact():
    return render_template("contact.html", user=app.user)

