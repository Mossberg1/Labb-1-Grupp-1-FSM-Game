from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from states import WAKEUP, STEALING, FLEE, SNEAK, CAUGHT, ESCAPED, START
from config import DRAGON


class ThiefFSM(FSMBehaviour):
    async def on_end(self):
        await self.agent.stop()
        

class Start(State):
    async def run(self):
        print("""
        === Tjuven och Draken ===
        Du är en tjuv som smyger in i drakens grotta för att stjäla guld.

        - För varje mynt du tar kan draken vakna.
        - Efter varje mynt väljer du: stjäla mer (y) eller fly (n).
        - Vaknar draken måste du fly och det finns en risk att draken fångar dig.

        Ju girigare du är, desto större risk. Lycka till!
        """)
        self.set_next_state(SNEAK)


class Sneak(State): # Start state
    async def run(self):
        msg = Message(to=DRAGON)
        msg.body = SNEAK
        await self.send(msg)
        # Antingen går thief över till stealing, eller så finns det en chans att man blir fångad
        reply = await self.receive(timeout=2)
        if reply and reply.body == WAKEUP:
            self.set_next_state(FLEE)
        else:
            self.set_next_state(STEALING)


class Stealing(State):
    async def run(self):
        msg = Message(to=DRAGON)
        msg.body = STEALING
        await self.send(msg)
        
        reply = await self.receive(timeout=2)
        if reply and reply.body == WAKEUP:
            self.set_next_state(FLEE)
        else:
            self.agent.add_gold(1)
            while True:
                steal_more = input("Vill du stjäla mer? (y/n): ")
                if steal_more == "y":
                    self.set_next_state(STEALING)
                    break
                elif steal_more == "n":
                    self.set_next_state(FLEE)
                    break
                

class Flee(State):
    async def run(self):
        msg = Message(to=DRAGON)
        msg.body = FLEE
        await self.send(msg)
        reply = await self.receive(timeout=2)
        if reply and reply.body == CAUGHT:
            self.set_next_state(CAUGHT)
        else:
            self.set_next_state(ESCAPED)


class Caught(State):
    async def run(self):
        print("Draken fångade tjuven!")


class Escaped(State):
    async def run(self):
        msg = Message(to=DRAGON)
        msg.body = ESCAPED
        await self.send(msg)
        print(f"Tjuven kom undan! Guld: {self.agent.gold}")


class Thief(Agent):
    async def setup(self):
        self.__gold = 0
        
        fsm = ThiefFSM()
        fsm.add_state(name=START, state=Start(), initial=True)
        fsm.add_state(name=SNEAK, state=Sneak())
        fsm.add_state(name=STEALING, state=Stealing())
        fsm.add_state(name=FLEE, state=Flee())
        fsm.add_state(name=CAUGHT, state=Caught())
        fsm.add_state(name=ESCAPED, state=Escaped())
        
        fsm.add_transition(source=START, dest=SNEAK)
        fsm.add_transition(source=SNEAK, dest=STEALING)
        fsm.add_transition(source=SNEAK, dest=FLEE)
        fsm.add_transition(source=STEALING, dest=STEALING)
        fsm.add_transition(source=STEALING, dest=FLEE)
        fsm.add_transition(source=FLEE, dest=CAUGHT)
        fsm.add_transition(source=FLEE, dest=ESCAPED)
        
        self.add_behaviour(fsm)
    
    
    @property
    def gold(self):
        return self.__gold


    def add_gold(self, n):
        if n <= 0:
            return
        self.__gold += n