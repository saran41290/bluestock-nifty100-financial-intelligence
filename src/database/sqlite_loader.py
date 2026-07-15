"""
sqlite_loader.py

Loads validated DataFrames into SQLite.
"""

from pathlib import Path
import sqlite3
import pandas as pd


class SQLiteLoader:

    def __init__(self, connection):

        self.connection = connection

    # --------------------------------------------------

    def insert_dataframe(
        self,
        dataframe: pd.DataFrame,
        table_name: str
    ):

        dataframe.to_sql(

            table_name,

            self.connection,

            if_exists="append",

            index=False

        )

    # --------------------------------------------------

    def count_rows(
        self,
        table_name: str
    ):

        cursor = self.connection.cursor()

        cursor.execute(

            f"SELECT COUNT(*) FROM {table_name}"

        )

        return cursor.fetchone()[0]

    # --------------------------------------------------

    def commit(self):

        self.connection.commit()

    # --------------------------------------------------

    def close(self):

        self.connection.close()