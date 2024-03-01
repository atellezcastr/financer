import sqlite3
import click
from flask import current_app, g
from typing import List, Dict, NoReturn

toa = {0: "Checkings", 1: "Savings", 2: "Joint"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo("Initialized the database")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_accounts(db, user_id: str, sort: bool = False) -> List:
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
    user: str,
    title: str,
    type_of_transaction: int,
    amount: float,
    description_of_transaction: str,
    comments: str,
    account_to_be_modified: str,
) -> List:
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


def get_posts(db, user_id: str) -> List:
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


def group_by_account_type(list_of_dicts: List) -> Dict:
    res = {}
    for elem in list_of_dicts:
        key, val = list(elem.keys()), list(elem.values())
        index_of_type = key.index("type_of_account")
        if val[index_of_type] in res:
            res[val[index_of_type]].append(elem)
        else:
            res[val[index_of_type]] = [elem]
    return res
