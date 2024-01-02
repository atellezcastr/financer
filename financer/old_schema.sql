DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS logs;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    type_of_transaction INT NOT NULL,
    amount REAL NOT NULL,
    description_of_transaction INT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
)
