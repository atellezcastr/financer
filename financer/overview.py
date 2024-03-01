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
from werkzeug.exceptions import abort
from financer.transactions import toes, tois, tots
from financer.accounts import toa

from financer.auth import login_required
from financer.db import get_db, get_accounts, get_posts, add_log_to_db

import datetime

bp = Blueprint("overview", __name__)


@bp.route("/")
def index():
    db = get_db()
    # Assuming g.user['id'] contains the current user's ID
    user_id = g.user["id"] if g.user else None
    posts = []
    accounts = []

    if user_id:
        posts = get_posts(db, user_id)
        accounts = get_accounts(db, user_id, sort=True)
    response = make_response(
        render_template("overview/index.html", posts=posts, accounts=accounts)
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        type_of_transaction = int(request.form["type_of_transaction"])
        title = request.form["title"]
        amount = float(request.form["amount"])
        comments = request.form["comments"]
        description_of_transaction = int(request.form["description_of_transaction"])
        account_to_be_modified = request.form["accounts"]
        error = None

        ## TODO whats best? to keep them as a must? for now, yes
        if not title:
            error = "Title is required"
        elif not amount:
            error = "Amount is required"

        if error:
            flash(error)
        else:
            accounts = add_log_to_db(
                get_db(),
                g.user["id"],
                title,
                type_of_transaction,
                amount,
                description_of_transaction,
                comments,
                account_to_be_modified,
            )
            posts = get_posts(get_db(), g.user["id"])
            return render_template(
                "overview/index.html", accounts=accounts, posts=posts
            )
    accounts = get_accounts(get_db(), g.user["id"])
    return render_template(
        "overview/create.html", toes=toes, tois=tois, tots=tots, accounts=accounts
    )
