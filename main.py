import spade
from thief import Thief
from dragon import Dragon

async def main():
    thief = Thief("thief@localhost", "password")
    dragon = Dragon("dragon@localhost", "password")
    await thief.start()
    await dragon.start()

if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=True)