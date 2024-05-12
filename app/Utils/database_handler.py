import mysql.connector

class DatabaseHandler:
    def __init__(self, host='localhost', user='root', password='secret', database='delmar'):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tbl_customer (name VARCHAR(255), phone VARCHAR(255), address VARCHAR(255))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tbl_report (name VARCHAR(255), title VARCHAR(255), note VARCHAR(255), timestamp VARCHAR(255))")

    def insert_customer(self, name, phone, address):
        sql = "INSERT INTO tbl_customer (name, phone, address) VALUES (%s, %s, %s)"
        val = (name, phone, address)
        self.cursor.execute(sql, val)
        self.db.commit()

    def insert_report(self, name, title, note, timestamp):
        sql = "INSERT INTO tbl_report (name, title, note, timestamp) VALUES (%s, %s, %s, %s)"
        val = (name, title, note, timestamp)
        self.cursor.execute(sql, val)
        self.db.commit()

    def close(self):
        self.db.close()