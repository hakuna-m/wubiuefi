"""User attribute RFC 2440.5.12

User attribute packets are more flexible versions of the user ID
packet. Right now, they aren't used for anything.
"""
from Packet import Packet


class UserAttribute(Packet):
    __doc__ = """User Attribute Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = UserAttributeBody(d)


class UserAttributeBody:
    """User Attribute

    :IVariables:
        - `_d`: string data used to fill UserID body
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def desc(self):
        if 'value' in self.__dict__:
            return ["value:%s" % self.value]
        else:
            return [""]

    def fill(self, d):
        self._d = d

