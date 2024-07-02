import psycopg2
from ..config import db_password
connection = psycopg2.connect(
    dbname="userbase",
    user="postgres",
    password="6023",#3-cr4td
    host="localhost"
)

cursor = connection.cursor()
cursor.execute("""CREATE TABLE users(
    user_id BIGINT PRIMARY KEY,
    name TEXT,
    root BOOL,
    spam_coins TEXT,
	delay INTEGER,
	time TIMESTAMP,
	warning_coins TEXT,
	limits TEXT,
	actions INTEGER,
	ban BOOL,
	date_of_registration TIMESTAMP
);""")