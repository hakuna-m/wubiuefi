"""Ordered dictionary class

Usage::

    >>> d = ordict()
    >>> d['a'] = 1
    >>> d['b'] = 2
    >>> d['c'] = 3

Access second element by keyword or index (in order of addition)::

    >>> d['b'] == d[1]
    True

Retrieve items ("list-ify") in order that they were added::

    >>> d.list()
    [1, 2, 3]

Retrieve keyword order (keyword list)::

    >>> d.keylist
    ['a', 'b', 'c']

Delete an entry by index::
    
    >>> del d[0]
    >>> d.list()
    [2, 3]
"""

class ordict(dict):
    """Ordered dictionary

    This is a dictionary subclass that supports *some* list-like
    operations. Basically, this is for convenience and will evolve as
    needed.
    """

    def __init__(self):
        "Initialize keylist."
        self.keylist = []
                                                                                                         
    def __setitem__(self, key, value):
        "Set keyword list."
        dict.__setitem__(self, key, value)
        if key not in self.keylist:
            self.keylist.append(key)
                                                                                                         
    def __getitem__(self, key):
        "Get dictionary item from keyword list index."
        try:
            return dict.__getitem__(self, key)

        except KeyError:

            if isinstance(key, int) and key < len(self.keylist):
                return dict.__getitem__(self, self.keylist[key])
            else:
                raise
                                                                                                         
    def __delitem__(self, key):
        "Delete keyword entry."
        try:
            dict.__delitem__(self, key)

        except KeyError:

            if isinstance(key, int) and key < len(self.keylist):
                dict.__delitem__(self, self.keylist[key])
            else:
                raise

        self.keylist.pop(key)

    def list(self):
        "Retrieve items ordered by key in keyword list."
        return [dict.__getitem__(self, key) for key in self.keylist]
