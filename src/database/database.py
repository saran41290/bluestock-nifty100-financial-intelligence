"""
database.py

Database Manager

Responsibilities
----------------
1. Create SQLite connection
2. Execute schema.sql
3. Return connection
4. Commit changes
5. Close connection
"""

from pathlib import Path
import sqlite3


class DatabaseManager:
    """
    SQLite Database Manager
    """

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.database_path = (
            self.project_root /
            "db" /
            "nifty100.db"
        )

        self.schema_path = (
            self.project_root /
            "db" /
            "schema.sql"
        )

        self.connection = None

    # --------------------------------------------------

    def connect(self):
        """
        Create SQLite connection.
        """

        self.connection = sqlite3.connect(self.database_path)

        return self.connection

    # --------------------------------------------------

    def create_tables(self):
        """
        Execute schema.sql
        """

        if self.connection is None:
            self.connect()

        with open(self.schema_path, "r", encoding="utf-8") as file:

            sql = file.read()

        self.connection.executescript(sql)

        self.connection.commit()

    # --------------------------------------------------

    def cursor(self):

        if self.connection is None:
            self.connect()

        return self.connection.cursor()

    # --------------------------------------------------

    def commit(self):

        if self.connection:

            self.connection.commit()

    # --------------------------------------------------

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None