"""Reserved

This packet class is used in test cases to store arbitrary data.

Technically, this packet "shouldn't be used." But since there isn't an
old version packet type set aside for "Private/Experimental" use, I'm 
using this class for testing. Ha.

Nothing special is performed by the class, and it's only "filled"
attribute is '_d'.

Example::

    >>> testbody = TestPGP('abc')
    >>> testbody._d
    'abc'
"""
from Packet import Packet


class Reserved(Packet):

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = ReservedBody(d)


class ReservedBody:

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        """restricted.fill(d)

        Fill the lonely attribute _d.

        Parameters::

            d  any kine data

        Return::

            absolutely nothing

        Example::

            >>> testbody = TestPGP()
            >>> testbody.fill('abc')
            >>> testbody._d
            'abc'
        """
        self._d = d
