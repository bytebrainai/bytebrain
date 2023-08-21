import multiprocessing
import core
from core.webserver import main
from core.discord import main


def start():
    p1 = multiprocessing.Process(target=core.webserver.main)
    p2 = multiprocessing.Process(target=core.discord.main)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
