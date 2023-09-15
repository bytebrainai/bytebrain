import multiprocessing
import core
from core.webservice import main
from core.discord import main


def start():
    load_sqlite3()
    p1 = multiprocessing.Process(target=core.webservice.main)
    p2 = multiprocessing.Process(target=core.discord.main)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


def load_sqlite3():
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pysqlite3-binary"]
    )
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
