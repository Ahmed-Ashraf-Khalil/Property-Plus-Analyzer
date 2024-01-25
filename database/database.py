import sqlite3


class DB:
    def __init__(self):
        pass

    @staticmethod
    def db_connect():
        conn = sqlite3.connect("../Properties.sqlite")

        return conn

    @staticmethod
    def db_close(conn):
        conn.close()

    @staticmethod
    def df_commit(conn):
        conn.commit()
