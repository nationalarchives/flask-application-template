from app.site import bp
from flask import render_template


@bp.route("/")
def hello_world():
    return render_template("welcome.html")


@bp.route("/alpha")
def alpha():
    return render_template("alpha.html")


@bp.route("/beta")
def beta():
    return render_template("beta.html")
