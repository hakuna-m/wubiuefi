"""User ID RFC 2440.5.11

The User ID packet contains identifying information about a key's owner.

"A User ID packet consists of data that is intended to represent the name and
email address of the key holder. By convention, it includes an RFC822 mail
name, but there are no restrictions on its content. The packet length in the
header specifies the length of the User ID. If it is text, it is encoded in
UTF-8."
"""
from Packet import Packet


class UserID(Packet):
    __doc__ = """User ID Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = UserIDBody(d)


class UserIDBody:
    """User ID

    :IVariables:
        - `value`: string User ID value
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
        """userid.fill(d)
        """
        self._d = self.value = d
