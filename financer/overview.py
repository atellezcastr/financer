from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from financer.transactions import toes, tois, tots
from financer.accounts import toa

from financer.auth import login_required
from financer.db import get_db

bp = Blueprint("overview", __name__)


@bp.route("/")
def index():
    db = get_db()
    # Assuming g.user['id'] contains the current user's ID
    user_id = g.user["id"]
    if user_id:
        posts = db.execute(
            "SELECT p.id, title, type_of_transaction, created, author_id, description_of_transaction, amount"
            " FROM logs p JOIN user u ON p.author_id = u.id"
            " WHERE u.id = ?"
            " ORDER BY created DESC",
            (user_id,),
        ).fetchall()
        accounts = db.execute(
            """SELECT id, name_of_account, balance, type_of_account
            FROM account
            WHERE user_id = ?""",
            (user_id,),
        ).fetchall()
        accounts = [
            {
                "id": account["id"],
                "name_of_account": account["name_of_account"],
                "balance": account["balance"],
                "type_of_account": toa[account["type_of_account"]],
            }
            for account in accounts
        ]
    return render_template("overview/index.html", posts=posts, accounts=accounts)


@bp.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        type_of_transaction = int(request.form["type_of_transaction"])
        title = request.form["title"]
        amount = float(request.form["amount"])
        comments = request.form["comments"]
        description_of_transaction = int(request.form["description_of_transaction"])
        error = None

        ## TODO whats best? to keep them as a must? for now, yes
        if not title:
            error = "Title is required"
        elif not amount:
            error = "Amount is required"

        if error:
            flash(error)
        else:
            print(type_of_transaction)
            db = get_db()
            db.execute(
                "INSERT into logs (author_id, title, type_of_transaction, amount, description_of_transaction, comments) VALUES (?,?,?,?,?,?)",
                (
                    g.user["id"],
                    title,
                    type_of_transaction,
                    amount,
                    description_of_transaction,
                    comments,
                ),
            )
            db.commit()
            return redirect(url_for("overview.index"))
    return render_template("overview/create.html", toes=toes, tois=tois, tots=tots)
