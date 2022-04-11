from flask import Flask
import sqlite3 as sql3

app = Flask(__name__)

class Query:
    all_messages = 'SELECT * FROM Messages'


@app.route("/")
def send_messages():
    db = sql3.connect('testdb.db')
    db_cursor = db.cursor()
    db_cursor.execute(Query.all_messages)
    a = db_cursor.fetchall()
    db.close()
    return '1'


if __name__ == "__main__":
    app.run(host='10.17.0.203', port=12345)
