import multiprocessing
import core
from core.webservice import main
from core.discord_bot import main


def start():
    p1 = multiprocessing.Process(target=core.webservice.main)
    p2 = multiprocessing.Process(target=core.discord_bot.main)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == "__main__":
    start()
