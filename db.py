import sqlite3

from datetime import datetime

DB_NAME = "data.db"


class DB:
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        try:
            self.conn = sqlite3.connect(DB_NAME)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(str(e))

    def insertData(self, data: dict) -> None:
        cam = "CAM " + str(data["cam"])
        age = data["age"]
        gender = data["gender"]
        dt = datetime.now()

        query = r'INSERT INTO infos("cam", "age", "gender", "datetime") VALUES(?, ?, ?, ?)'

        self.cursor.execute(query, (cam, age, gender, dt))
        self.conn.commit()

    def fetchAll(self) -> list[tuple]:
        query = "SELECT * FROM infos ORDER BY id DESC"
        result = self.cursor.execute(query).fetchall()
        return result

    def clearDatabase(self):
        self.cursor.execute("DELETE FROM infos")
        self.cursor.execute("DELETE FROM sqlite_sequence where name='infos'")
        self.conn.commit()


if __name__ == "__main__":
    db = DB()
    db.connect()
    data = db.fetchAll()
    print(data)
