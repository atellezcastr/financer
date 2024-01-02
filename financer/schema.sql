DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS account;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE transaction_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL
);

INSERT INTO transaction_types (type_name) VALUES ('Income'), ('Expense');

CREATE TABLE transaction_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description_name TEXT NOT NULL
);

-- Populate transaction descriptions as needed

CREATE TABLE account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_of_account TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    balance REAL NOT NULL DEFAULT 0,
    type_of_account INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    type_of_transaction INTEGER NOT NULL,
    amount REAL NOT NULL,
    description_of_transaction INTEGER NOT NULL,
    comments TEXT,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (type_of_transaction) REFERENCES transaction_types (id),
    FOREIGN KEY (description_of_transaction) REFERENCES transaction_descriptions (id)
);