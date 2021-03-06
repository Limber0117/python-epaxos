class CoException(Exception):
    def __init__(self, val=None):
        self.val = val


class CoPause(CoException):
    pass


class CoExit(CoException):
    pass


NOTHING = object()


def coroutiner(corout, send=NOTHING, router=None):
    while True:
        try:
            send_next = send
            send = NOTHING

            if send_next != NOTHING:
                nxt = corout.send(send_next)
            else:
                nxt = next(corout)

            if router:
                send = router(nxt)
            else:
                raise CoPause(nxt)
        except CoPause as e:
            return e.val
        except StopIteration:
            raise CoExit()

