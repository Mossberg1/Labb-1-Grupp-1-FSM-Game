import spade
from thief import Thief
from dragon import Dragon
from config import THIEF, DRAGON

async def main():
    thief = Thief(THIEF, "password")
    dragon = Dragon(DRAGON, "password")
    await dragon.start()  # dragon first, so it's listening when the thief sneaks in
    await thief.start()
    await spade.wait_until_finished([thief, dragon])

if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)