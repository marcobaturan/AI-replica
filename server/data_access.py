import sqlite3
import time
import uuid
from server.read_config import config

DB_PATH = config['server']['db_path']

db_connection = sqlite3.connect(DB_PATH)

def does_table_exist(table_name):
  db = db_connection.cursor()
  result = db.execute(f"SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='{table_name}';") \
    .fetchone()
  db.close()
  return result[0] == 1

def create_messages_table():
  db = db_connection.cursor()
  result = db.execute('''CREATE TABLE Messages
    (id text, text text, date integer, user_id text)''')
  db_connection.commit()
  db.close()

def create_users_table():
  db = db_connection.cursor()
  result = db.execute('''CREATE TABLE Users
    (id text, name text)''')
  db_connection.commit()
  db.close()

def ensure_tables_exist():
  db = db_connection.cursor()
  if not does_table_exist("Messages"):
    create_messages_table()  
  if not does_table_exist("Users"):
    create_users_table()
  db.close()

def get_messages():
  db = db_connection.cursor()
  result = db.execute('SELECT * FROM Messages')
  for row in result:
    print(row)
  db.close()

def get_user_messages(user_id):
  db = db_connection.cursor()
  result = db.execute(f'SELECT * FROM Messages WHERE user_id="{user_id}"')
  for row in result:
    print(row)
  db.close()

def add_message(text, user_id):
  db = db_connection.cursor()
  
  current_time_ms = int(time.time_ns()/1000)
  id = str(uuid.uuid4())
  escaped_text = text.replace('"', '\\"')
  print(f"INSERT INTO Messages VALUES ('{id}','{escaped_text}',{current_time_ms},'{user_id}')")
  db.execute(f"INSERT INTO Messages VALUES ('{id}','{escaped_text}',{current_time_ms},'{user_id}')")
  db_connection.commit()
  db.close()
