import MySQLdb


class MySQL(object):
    def __init__(self):
        self.host = "localhost"
        self.username = "root"
        self.password = ""
        self.db = MySQLdb.connect(self.host, self.username, self.password, "information_schema")
        # self.db = MySQLdb.connect(self.host, self.username, self.password, db_name)
        self.cursor = self.db.cursor()

    def create_database(self, database_name):
        sql = "CREATE DATABASE IF NOT EXISTS " + database_name + ";"
        try:
            self.cursor.execute(sql)
            self.use_database(database_name)
        except Exception as error:
            print(error)
            exit(-1)

    def use_database(self, database_name):
        sql = "USE " + database_name + ";"
        try:
            self.cursor.execute(sql)
        except Exception as error:
            print(error)
            exit(-1)

    def create_table(self, table_name, columns):
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + " (" + columns + ");"
        print(sql)
        self.execute_query(sql)

    def execute_query(self, sql):
        try:
            self.cursor.execute(sql)

            if (sql[:6].lower() == "select" or sql[1:7].lower() == "select"):
                # print("in")
                return self.cursor.fetchall()
            self.db.commit()
        except Exception as error:
            print(error)
            self.db.rollback()

    def close_db(self):
        self.db.close()
