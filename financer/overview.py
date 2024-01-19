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
    user_id = g.user["id"] if g.user else None
    posts = []
    accounts = []

    if user_id:
        posts = db.execute(
            "SELECT p.id, title, type_of_transaction, created, author_id, description_of_transaction, amount"
            " FROM logs p JOIN user u ON p.author_id = u.id"
            " WHERE u.id = ?"
            " ORDER BY created DESC",
            (user_id,),
        ).fetchall()
        accounts = get_accounts(db, user_id)
    return render_template("overview/index.html", posts=posts, accounts=accounts)


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
            return render_template(
                "overview/index.html", posts=[], accounts=accounts
            )
    accounts = get_accounts(get_db(), g.user["id"])
    return render_template(
        "overview/create.html", toes=toes, tois=tois, tots=tots, accounts=accounts
    )


def get_accounts(db, user_id):
    query = """SELECT id, name_of_account, balance, type_of_account
            FROM account
            WHERE user_id = ?"""
    accounts = db.execute(
        query,
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
    return accounts


Copy code
def add_log_to_db(
    db,
    user,
    title,
    type_of_transaction,
    amount,
    description_of_transaction,
    comments,
    account_to_be_modified,
):
    add_log_query = "INSERT into logs (author_id, title, type_of_transaction, amount, description_of_transaction, comments) VALUES (?,?,?,?,?,?)"
    transaction = db.execute(
        add_log_query,
        (
            g.user["id"],
            title,
            type_of_transaction,
            amount,
            description_of_transaction,
            comments,
        ),
    )

    # Update account balance
    affect_account_query = "UPDATE account SET balance = balance + ? WHERE id = ?"
    affect_account_transaction = db.execute(
        affect_account_query, (amount, account_to_be_modified)
    )

    # Fetch the updated account information after the balance update
    accounts = get_accounts(db, g.user["id"])

    # Commit changes to the database
    db.commit()

    return accounts