from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from states import CAUGHT, STEALING, WAKEUP, SLEEP, ESCAPED, SNEAK
from config import THIEF
import random


class DragonFSM(FSMBehaviour):
    async def on_end(self):
        await self.agent.stop()


class Sleep(State):
    async def run(self):
        msg = await self.receive(timeout=2)

        if msg and msg.body == ESCAPED:
            return
        
        # TODO: Ändra senare
        wakeup = random.random() < 0.25  # 75% chance the thief gets away with it (testing value)
        if msg and (msg.body == STEALING or msg.body == SNEAK) and wakeup:
            print("Draken har vaknat!")
            msg = Message(to=THIEF)
            msg.body = WAKEUP
            await self.send(msg)
            self.set_next_state(WAKEUP)
        else:
            self.set_next_state(SLEEP)


class Wakeup(State):
    async def run(self):
        caught = random.choice([True, False]) # 50% chans att fånga tjuven.
        if caught:
            msg = Message(to=THIEF)
            msg.body = CAUGHT
            await self.send(msg)


class Dragon(Agent):
    async def setup(self):
        fsm = DragonFSM()
        fsm.add_state(name=SLEEP, state=Sleep(), initial=True)
        fsm.add_state(name=WAKEUP, state=Wakeup())
        fsm.add_transition(source=SLEEP, dest=SLEEP)
        fsm.add_transition(source=SLEEP, dest=WAKEUP)
        self.add_behaviour(fsm)