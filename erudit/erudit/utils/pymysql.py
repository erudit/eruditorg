import pymysql


class pymysql_connection():

    def __init__(self, host=None, username=None, password=None, database=None):
        self.username = username
        self.password = password
        self.host = host
        self.database = database

    def __enter__(self):

        self.conn = pymysql.connect(
            host=self.host,
            unix_socket='/tmp/mysql.sock',
            user=self.username,
            passwd=self.password,
            db=self.database,
        )

        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.close()
