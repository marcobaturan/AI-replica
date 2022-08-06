import sqlite3
from server.read_config import config

DB_PATH = config['server']['db_path']

db_connection = sqlite3.connect(DB_PATH)

def does_table_exist(table_name):
  db = db_connection.cursor()
  result = db.execute(f"SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';") \
    .fetchone()
  return result[0] == 1

def create_user_table():
  db = db_connection.cursor()
  result = db.execute('''CREATE TABLE Users
    (date text, trans text, symbol text, qty real, price real)''')

def ensure_tables_exist():
  db = db_connection.cursor()
  if not does_table_exist("Users"):
    create_user_table()

def get_users():
  db = db_connection.cursor()
  result = db.execute('SELECT * FROM Users')
  for row in result:
    print(row)
