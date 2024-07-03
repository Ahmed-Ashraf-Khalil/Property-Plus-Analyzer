import sqlite3

class DataBase:

    @staticmethod
    def connect_data_base():
        data_base_connection = sqlite3.connect("DataBase/Properties.sqlite")

        return data_base_connection

    @staticmethod
    def close_data_base(conn):
        data_base_connection.close()

    @staticmethod
    def commit_data_base(conn):
        data_base_connection.commit()