import os
import unittest

from ratestask.db import DBAPI


class TestBase(unittest.TestCase):

    def setUp(self):
        db_uri = os.getenv("DATABASE_URI")

        db = DBAPI(db_uri)
        db_conn = db.get_db_conn()

        self.db = db
        self.db_conn = db_conn
        self.db_uri = db_uri

        self._setup_tables()

    def tearDown(self):
        self._drop_tables()
        self.db_conn.close()

    def _setup_tables(self):
        self._drop_tables()

        sql_script = os.path.join(
            os.path.dirname(__file__), "schema", "create_tables.sql"
        )
        with open(sql_script) as f:
            cursor = self.get_db_cursor()
            cursor.execute(f.read())
            cursor.connection.commit()

    def _drop_tables(self):
        sql_script = os.path.join(
            os.path.dirname(__file__), "schema", "drop_tables.sql"
        )
        with open(sql_script) as f:
            cursor = self.db_conn.cursor()
            cursor.execute(f.read())
            cursor.connection.commit()

    def get_db_cursor(self):
        return self.db_conn.cursor()

    def create_db_entries(self, db_cursor, table_name, data_dicts):
        """
        Inserts DB rows/entries into a given table.
        """
        columns = list(data_dicts[0].keys())
        values = [
            tuple(item[column] for column in columns)
            for item in data_dicts
        ]

        for value in values:
            columns_str = ", ".join(columns)
            values_placeholders = ", ".join("%s" for _ in columns)

            insert_stmt = "INSERT INTO %s (%s) VALUES (%s)" % (
                table_name, columns_str, values_placeholders
            )
            db_cursor.execute(insert_stmt, value)

        db_cursor.connection.commit()
