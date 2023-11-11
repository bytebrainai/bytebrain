import multiprocessing
import core
from core.bots.web.webservice import main
from core.bots.discord.discord_bot import main


def start():
    p1 = multiprocessing.Process(target=core.bots.web.webservice.main)
    p2 = multiprocessing.Process(target=core.bots.discord.discord_bot.main)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == "__main__":
    start()
