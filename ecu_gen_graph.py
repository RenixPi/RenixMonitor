from transitions.extensions import GraphMachine as Machine
from functools import partial
from receiver import Receiver


class Model:

    def clear_state(self, deep=False, force=False):
        print("Clearing state...")
        return True


model = Model()
machine = Machine(model=model,
                  transitions=Receiver.transitions,
                  initial=Receiver.States.UNKNOWN)

model.get_graph().draw('renix_receive_diagram.png', prog='dot')
