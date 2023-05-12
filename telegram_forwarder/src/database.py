import threading
import sqlite3

from time import time
from . import config

from queue import Queue


class Datasource(threading.Thread):
    def __init__(self):
        self.init()

    def init(self):
        self.db = sqlite3.connect(config.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS chat(id INTEGER PRIMARY KEY AUTOINCREMENT, chatid VARCHAR(255) NOT NULL, messageid BIGINT NOT NULL, sent INTEGER NOT NULL DEFAULT 0, fetchdate DOUBLE NOT NULL)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS chat_message ON chat (chatid,messageid)"
        )
        self.db.commit()
        cursor.close()

    def insert_chat(self, chat_id: str, message_id: str):
        cursor = self.db.cursor()
        query = "INSERT INTO chat (chatid, messageid, fetchdate) VALUES (?, ?, ?)"
        try:
            cursor.execute(query, (chat_id, message_id, time()))
            self.db.commit()
        except sqlite3.IntegrityError:
            pass
        cursor.close()

    def get_media_messages(self, chat_id: str) -> list[str]:
        cursor = self.db.cursor()
        query = "SELECT messageid FROM chat WHERE chatid = ?"
        cursor.execute(query, (chat_id,))
        self.db.commit()
        data = cursor.fetchall()
        cursor.close()
        return [x[0] for x in data]

    def get_first_message(self, chat_id: str) -> int:
        cursor = self.db.cursor()
        query = "SELECT messageid FROM chat WHERE chatid = ? ORDER BY id LIMIT 1"
        cursor.execute(query, (chat_id,))
        self.db.commit()
        data = cursor.fetchone()
        cursor.close()
        return data

    def get_last_date(self) -> float:
        cursor = self.db.cursor()
        query = "SELECT fetchdate FROM chat ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        self.db.commit()
        data = cursor.fetchone()
        cursor.close()
        return data

    def mark_as_sent(self, chat_id: str, message_id: str):
        cursor = self.db.cursor()
        query = "UPDATE chat SET sent = 1 WHERE messageid = ? AND chatid = ?"
        cursor.execute(query, (message_id, chat_id))
        self.db.commit()
        cursor.close()

    def check_if_sent(self, chat_id: str, message_id: str) -> bool:
        cursor = self.db.cursor()
        query = "SELECT sent FROM chat WHERE messageid = ? AND chatid = ?"
        cursor.execute(query, (message_id, chat_id))
        self.db.commit()
        data = cursor.fetchone()[0]
        data = data == 1
        cursor.close()
        return data
    
    def run(self):
        self.init()
