import sqlite3 as sql3


class Query:
    all_messages = 'SELECT * FROM Messages'


def send_messages():

    def create_message_dict(message, headers):
        ans = dict()
        for key, data in zip(headers, message):
            ans[key] = data
        return ans

    db = sql3.connect('testdb.db')
    db_cursor = db.cursor()
    db_cursor.execute(Query.all_messages)
    raw_messages = db_cursor.fetchall()
    headers = [i[0] for i in db_cursor.description]
    messages = list()
    for message in raw_messages:
        message.
    db.close()
    return '1'


send_messages()
