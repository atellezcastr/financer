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
from financer.db import get_db

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


def get_accounts(db, user_id, sort=False):
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
    if sorted:
        # accounts = sorted(accounts, key=lambda d: d["type_of_account"])
        accounts = group_by_account_type(accounts)
    return accounts


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
    try:
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
    except Exception as e:
        print(f"There was an error adding the log to the database: {str(e)}")
        db.rollback()
        return None
    # Update account balance
    try:
        affect_account_query = (
            "UPDATE account SET balance = balance + ? WHERE name_of_account = ?"
        )
        affect_account_transaction = db.execute(
            affect_account_query, (amount, account_to_be_modified)
        )
    except Exception as e:
        print(f"Error in updating the account amount {str(e)}")
        db.rollback()
        return None
    # Fetch the updated account information after the balance update

    # Commit changes to the database
    db.commit()
    accounts = get_accounts(db, g.user["id"])

    return accounts


def get_posts(db, user_id):
    QUERY = """ SELECT p.id, title, type_of_transaction, created, author_id, description_of_transaction, amount
             FROM logs p JOIN user u ON p.author_id = u.id
             WHERE u.id = ?
             ORDER BY created DESC"""

    posts = db.execute(
        QUERY,
        (user_id,),
    ).fetchall()

    date_input_format = "%y-%m-%d %H:%M:%S"
    date_output_format = "%a %d %b %Y, %I:%M%p"

    new_posts = [
        {
            "title": post["title"],
            "type_of_transaction": post["type_of_transaction"],
            "amount": post["amount"],
            "created": post["created"].strftime(date_output_format),
            "description_of_transaction": post["description_of_transaction"],
        }
        for post in posts
    ]
    return new_posts


def group_by_account_type(list_of_dicts):
    res = {}
    for elem in list_of_dicts:
        key, val = list(elem.keys()), list(elem.values())
        index_of_type = key.index("type_of_account")
        if val[index_of_type] in res:
            res[val[index_of_type]].append(elem)
        else:
            res[val[index_of_type]] = [elem]
    return res
