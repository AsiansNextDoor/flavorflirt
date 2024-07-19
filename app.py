#!/usr/bin/env python3

import csv
import pathlib
from flask import Flask, make_response, render_template, request, redirect, url_for
from crud import read

from werkzeug.utils import secure_filename


def create_app():
    app = Flask(__name__)
    # with open("archive/dishes.csv", "r") as f:
    #     app.data = list(csv.DictReader(f, delimiter=","))
    app.data = list(read("food.db", "dishes"))[:10]
    return app


app = create_app()


@app.route("/")
def index():
    return render_template("index.html", data=app.data)


@app.post("/upload")
def upload():
    f = request.files["file"]
    f.save(
        pathlib.Path(__file__).parent.absolute()
        / pathlib.Path("uploads")
        / pathlib.Path(secure_filename(f.filename))
    )

    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("display_file", secure_filename(f.filename))
    return resp
