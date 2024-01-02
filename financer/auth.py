import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from financer.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name_of_new_account = request.form["name_of_account"]
        type_of_account = request.form["type_of_account"]
        initial_amount = request.form["initial_amount"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"

        if not name_of_new_account:
            flash("Defaulting name of account")
            if not type_of_account:
                name_of_new_account = "Default Chequings Account"
            else:
                name_of_new_account = (
                    "Default Chequings Account"
                    if int(type_of_account) == 0
                    else "Default Savings Account"
                )
        if not initial_amount:
            initial_amount = 0
        if not error:
            if create_user_account(
                db,
                username,
                password,
                name_of_new_account,
                type_of_account,
                initial_amount,
            ):
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        flash(error)
    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


def create_user_account(
    db,
    username: str,
    password: str,
    name_of_account: str,
    type_of_account: int,
    initial_amount: float,
):
    try:
        # Begin a transaction
        db.execute("BEGIN TRANSACTION")

        # Insert the user into the "user" table
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )

        # Retrieve the ID of the recently inserted user
        user_id = db.execute(
            "SELECT id FROM user WHERE username = ?", (username,)
        ).fetchone()[0]

        # Insert the account into the "account" table with the user ID
        db.execute(
            "INSERT INTO account (user_id, name_of_account, balance, type_of_account) VALUES (?,?,?,?)",
            (user_id, name_of_account, float(initial_amount), int(type_of_account)),
        )

        # Commit the transaction if everything is successful
        db.commit()
        print("Commit successful")

    except db.IntegrityError:
        # Handle integrity error (e.g., duplicate username)
        print("Error on integrity")
        error = f"User {username} is already registered"

        # Rollback the transaction to undo any changes
        db.execute("ROLLBACK")
    else:
        return True
