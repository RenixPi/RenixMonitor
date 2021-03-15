from receiver import Receiver
from assertpy import assert_that


def test_unknown_state_transition():
    r = Receiver()
    r.receive_zero()
    assert_that(r.state).is_equal_to(Receiver.States.UNKNOWN)


def test_normal_frame():

    r = Receiver()
    frame = bytearray([0xFF, 0x00, 0x01, 0x02, 0x03, 0xFF, 0x00])
    for f in frame:
        r.process(f)

    print("current state: {}".format(r.state))
    assert_that(r.frame).is_equal_to(bytearray([0x1, 0x2, 0x3]))

def test_bad_frame_value():

    r = Receiver()
    frame = bytearray([0xFF, 0x00, 0x01, 0x02, 0xFF, 0x00])
    for f in frame:
        r.process(f)

