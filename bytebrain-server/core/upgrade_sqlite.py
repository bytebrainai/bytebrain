import sqlite3
import subprocess
import sys

def upgrade_sqlite_version():
    if sqlite3.sqlite_version_info < (3, 35, 0):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pysqlite3-binary"]
        )
        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
