from transitions import Machine
from frame import Frame
import enum
import logging

logger = logging.getLogger('ecu.receiver')


class EmptyFrame(Exception):
    pass


class InvalidByte(Exception):
    pass


class Receiver:

    class States(enum.Enum):
        UNKNOWN = 0
        START = 1
        DATA = 2
        MARK = 3
        WAIT = 4
        ERROR = 5

    transitions = [
        {
            'trigger': 'receive_mark',
            'source': [States.UNKNOWN, States.DATA, States.WAIT],
            'dest': States.MARK
        },
        {
            'trigger': 'receive_mark',
            'source': States.MARK,
            'dest': States.DATA
        },
        {
            'trigger': 'receive_zero',
            'source': States.UNKNOWN,
            'dest': States.UNKNOWN
        },
        {
            'trigger': 'receive_zero',
            'source': States.MARK,
            'dest': States.START
        },
        {
            'trigger': 'receive_zero',
            'source': [States.START, States.DATA],
            'dest': States.DATA
        },
        {
            'trigger': 'receive_value',
            'source': [States.START, States.DATA],
            'dest': States.DATA
        },
        {
            'trigger': 'receive_value',
            'source': States.UNKNOWN,
            'dest': States.UNKNOWN
        }
    ]

    def __init__(self, frame_receiver=None, initial=States.UNKNOWN):

        self.frame = None
        self.frame_receiver = frame_receiver
        self.frame_buffer = bytearray()
        # logging.getLogger('transitions').addHandler(logging.NullHandler())
        self.machine = Machine(model=self,
                               states=Receiver.States,
                               transitions=self.transitions,
                               send_event=True,
                               initial=initial)

    def on_enter_START(self, event):
        if self.frame_buffer:
            self.frame = Frame(self.frame_buffer)
            if self.frame_receiver:
                self.frame_receiver(self.frame)
        self.frame_buffer = bytearray()

    def on_enter_WAIT(self, event):
        self.frame = self.frame_buffer

    def on_enter_DATA(self, event):
        self.frame_buffer.append(event.kwargs.get('rcvd')[0])

    def process(self, value):

        pre_state = self.state
        v = int.from_bytes(value, byteorder='big')

        if v == 0x00:
            self.receive_zero(rcvd=b'\x00')
        elif v == 0xFF:
            self.receive_mark(rcvd=b'\xFF')
        elif 0 < v < 0xFF:
            self.receive_value(rcvd=value)
        else:
            raise InvalidByte("value is 0x{:02X}".format(v))

        post_state = self.state
        logger.debug("rcv: 0x{:02X} pre: {} post: {}".format(v, pre_state, post_state))
