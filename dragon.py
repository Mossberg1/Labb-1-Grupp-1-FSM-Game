from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from states import CAUGHT, STEALING, WAKEUP, SLEEP, ESCAPED, SNEAK, FLEE
from config import THIEF
from termcolor import colored
import random


has_printed_yellow_warning = False
has_printed_red_warning = False


def print_dragon_wakup_state(chance):
    global has_printed_yellow_warning, has_printed_red_warning
    if 0.25 <= chance < 0.3 and not has_printed_yellow_warning:
        print(colored("Draken grymtar och vänder sig i sömnen...", "yellow"))
        has_printed_yellow_warning = True
    elif chance >= 0.3 and not has_printed_red_warning:
        print(colored("Draken är nästan vaken!", "red"))
        has_printed_red_warning = True


class DragonFSM(FSMBehaviour):
    async def on_end(self):
        await self.agent.stop()


class Sleep(State):
    async def run(self):
        msg = await self.receive(timeout=2)

        if msg and msg.body == ESCAPED:
            self.set_next_state(None) # VIKTIGT måste sätta None för att avsluta spelet när tjuven flyr.
            return
        
        wakeup = random.random() < self.agent.chance_to_wakeup
        
        print_dragon_wakup_state(self.agent.chance_to_wakeup)
        
        if msg and msg.body == STEALING and msg.body != SNEAK:
            self.agent.increase_chance_to_wakeup() 

        if msg and (msg.body == STEALING or msg.body == SNEAK or msg.body == FLEE) and wakeup:
            print("Draken har vaknat!")
            if msg.body != FLEE:
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
        self.__chance_to_wakeup = 0.05
        
        fsm = DragonFSM()
        fsm.add_state(name=SLEEP, state=Sleep(), initial=True)
        fsm.add_state(name=WAKEUP, state=Wakeup())
        fsm.add_transition(source=SLEEP, dest=SLEEP)
        fsm.add_transition(source=SLEEP, dest=WAKEUP)
        self.add_behaviour(fsm)
    
    
    def increase_chance_to_wakeup(self):
        chance = self.__chance_to_wakeup + 0.05
        self.__chance_to_wakeup = min(chance, 0.5)
    
    
    @property
    def chance_to_wakeup(self):
        return self.__chance_to_wakeup