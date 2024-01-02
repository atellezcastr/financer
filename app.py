from flask import Flask, render_template, url_for, redirect


app = Flask(__name__)


@app.route("/")
def index():
    # return "<p>Hello World</p>"
    return render_template("landing_page.html")


@app.route("/test")
def test():
    return "sucessfull redirect"
