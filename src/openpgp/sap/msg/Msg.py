"""Parent Message Class

So far all the `Msg` class does is take care of the ``_d`` attribute
for message instances by concatenating all the packet data in the
message sequence ``_seq``.
"""
# so that we can test to see if sequence items are members of Msg subclass
class Msg:
    """Parent Message Class
    """
    def rawstr(self):

        return ''.join([x.rawstr() for x in self.seq()])

    def seq(self):
        return self._seq

    def __nonzero__(self): # egads, shouldn't this be set by default?
        return True

    def __eq__(self, other):

        if self.rawstr() == other.rawstr():

            return True
        else:

            return False

    def __ne__(self, other):

        if self.rawstr() != other.rawstr():

            return True
        else:

            return False

