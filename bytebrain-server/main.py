# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
