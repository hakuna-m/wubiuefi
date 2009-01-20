"""Test packet

This packet class is used in test cases to store arbitrary data.

Nothing special is performed by the class, and it's only "filled"
attribute is '_d'.

Example::

    >>> testbody = TestPGP('abc')
    >>> testbody._d
    'abc'
"""
import Packet

class TestPGP(Packet.Packet):

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = TestPGPBody(d)


class TestPGPBody:
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        """body.fill(d)

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
