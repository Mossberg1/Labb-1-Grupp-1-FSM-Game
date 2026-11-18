# William Mossberg (h24wilmo)
# Viktor Eriksson (h24verik)
# Oskar Johansson (h24oskjo) 
# Tom Bergman (h24tober)
# Tobias Söder (h24tobso)

import spade
from thief import Thief
from dragon import Dragon
from config import THIEF, DRAGON
import logging


logging.getLogger("spade.Agent").setLevel(logging.ERROR) # Ta bort SPADE loggar från terminalen.


async def main():
    thief = Thief(THIEF, "password")
    dragon = Dragon(DRAGON, "password")
    await dragon.start()
    await thief.start()
    await spade.wait_until_finished([thief, dragon])


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)