CREATE TABLE IF NOT EXISTS inventory (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
condition text NOT NULL,
owner text NOT NULL,
request text NOT NULL,
status text NOT NULL,
request_quantity text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS plan (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
quantity text NOT NULL,
cost text NOT NULL,
provider text NOT NULL
);

CREATE TABLE IF NOT EXISTS report (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username text NOT NULL,
admin_name text NOT NULL,
item_name text NOT NULL,
quantity text NOT NULL,
status text NOT NULL,
text text NOT NULL
);

CREATE TABLE IF NOT EXISTS wanted (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
username text NOT NULL,
item_name text NOT NULL,
quantity text NOT NULL,
status text NOT NULL
);