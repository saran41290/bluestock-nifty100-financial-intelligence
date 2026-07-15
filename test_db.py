from src.database.database import DatabaseManager

db = DatabaseManager()

db.connect()

db.create_tables()

print("Database Created Successfully")

db.close()