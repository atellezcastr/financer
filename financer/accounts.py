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
from financer.db import get_db, get_accounts

bp = Blueprint("accounts", __name__, template_folder="accounts")

toa = {0: "Checkings", 1: "Savings", 2: "Joint"}


@bp.route("/index", methods=["GET"])
@login_required
def index():
    user_id = g.user["id"]
    accounts = get_accounts(get_db(), user_id, sort=True)
    return render_template("accounts/index.html", accounts=accounts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    return render_template("accounts/create.html")
