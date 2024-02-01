from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    make_response,
)

from financer.auth import login_required
from financer.db import get_db

bp = Blueprint("account_management", __name__, template_folder="accounts")

toa = {0: "Checkings", 1: "Savings", 2: "Joint"}


@bp.route("/index", methods=["GET"])
@login_required
def index():
    return render_template("accounts/index.html")


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    return render_template("accounts/create.html")
