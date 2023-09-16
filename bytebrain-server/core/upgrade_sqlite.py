def upgrade_sqlite_version():
    import sqlite3
    if sqlite3.sqlite_version_info < (3, 35, 0):
        import sys

        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
