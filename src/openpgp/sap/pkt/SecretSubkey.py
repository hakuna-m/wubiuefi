"""Secret subkey RFC 2440.5.5.1.4

Secret subkey packets are just like secret key packets, with one
difference: they are subkeys.
"""

from SecretKey import SecretKey, SecretKeyBody


class SecretSubkey(SecretKey):
    __doc__ = """Secret Subkey Packet
    """ + SecretKey._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = SecretSubkeyBody(d)


class SecretSubkeyBody(SecretKeyBody):
    _title = """Secret Subkey
    """
    _ivars = SecretKeyBody._ivars
    _notes = SecretKeyBody._notes
    __doc__ = ''.join([_title, _ivars, _notes])
    
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass
