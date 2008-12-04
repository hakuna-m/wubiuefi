# Written by Bram Cohen
# see LICENSE.txt for license information

from random import randrange, shuffle, choice

class PiecePicker:
    def __init__(self, numpieces, rarest_first_cutoff = 1):
        self.rarest_first_cutoff = rarest_first_cutoff
        self.numpieces = numpieces
        self.interests = [range(numpieces)]
        self.pos_in_interests = range(numpieces)
        self.numinterests = [0] * numpieces
        self.started = []
        self.seedstarted = []
        self.numgot = 0
        self.scrambled = range(numpieces)
        shuffle(self.scrambled)

    def got_have(self, piece):
        if self.numinterests[piece] is None:
            return
        numint = self.numinterests[piece]
        if numint == len(self.interests) - 1:
            self.interests.append([])
        self.numinterests[piece] += 1
        self._shift_over(piece, self.interests[numint], self.interests[numint + 1])

    def lost_have(self, piece):
        if self.numinterests[piece] is None:
            return
        numint = self.numinterests[piece]
        self.numinterests[piece] -= 1
        self._shift_over(piece, self.interests[numint], self.interests[numint - 1])

    def _shift_over(self, piece, l1, l2):
        p = self.pos_in_interests[piece]
        l1[p] = l1[-1]
        self.pos_in_interests[l1[-1]] = p
        del l1[-1]
        newp = randrange(len(l2) + 1)
        if newp == len(l2):
            self.pos_in_interests[piece] = len(l2)
            l2.append(piece)
        else:
            old = l2[newp]
            self.pos_in_interests[old] = len(l2)
            l2.append(old)
            l2[newp] = piece
            self.pos_in_interests[piece] = newp

    def requested(self, piece, seed = False):
        if piece not in self.started:
            self.started.append(piece)
        if seed and piece not in self.seedstarted:
            self.seedstarted.append(piece)

    def complete(self, piece):
        assert self.numinterests[piece] is not None
        self.numgot += 1
        l = self.interests[self.numinterests[piece]]
        p = self.pos_in_interests[piece]
        l[p] = l[-1]
        self.pos_in_interests[l[-1]] = p
        del l[-1]
        self.numinterests[piece] = None
        try:
            self.started.remove(piece)
            self.seedstarted.remove(piece)
        except ValueError:
            pass

    def next(self, havefunc, seed = False):
        bests = None
        bestnum = 2 ** 30
        if seed:
            s = self.seedstarted
        else:
            s = self.started
        for i in s:
            if havefunc(i):
                if self.numinterests[i] < bestnum:
                    bests = [i]
                    bestnum = self.numinterests[i]
                elif self.numinterests[i] == bestnum:
                    bests.append(i)
        if bests:
            return choice(bests)
        if self.numgot < self.rarest_first_cutoff:
            for i in self.scrambled:
                if havefunc(i):
                    return i
            return None
        for i in xrange(1, min(bestnum, len(self.interests))):
            for j in self.interests[i]:
                if havefunc(j):
                    return j
        return None

    def am_I_complete(self):
        return self.numgot == self.numpieces

    def bump(self, piece):
        l = self.interests[self.numinterests[piece]]
        pos = self.pos_in_interests[piece]
        del l[pos]
        l.append(piece)
        for i in range(pos,len(l)):
            self.pos_in_interests[l[i]] = i

def test_requested():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.requested(1)
    p.requested(1)
    p.requested(3)
    p.requested(0)
    p.requested(6)
    v = _pull(p)
    assert v[:2] == [1, 3] or v[:2] == [3, 1]
    assert v[2:4] == [0, 6] or v[2:4] == [6, 0]
    assert v[4:] == [2, 4] or v[4:] == [4, 2]

def test_change_interest():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.lost_have(2)
    p.lost_have(6)
    v = _pull(p)
    assert v == [0, 4] or v == [4, 0]

def test_change_interest2():
    p = PiecePicker(9)
    p.complete(8)
    p.got_have(0)
    p.got_have(2)
    p.got_have(4)
    p.got_have(6)
    p.lost_have(2)
    p.lost_have(6)
    v = _pull(p)
    assert v == [0, 4] or v == [4, 0]

def test_complete():
    p = PiecePicker(1)
    p.got_have(0)
    p.complete(0)
    assert _pull(p) == []
    p.got_have(0)
    p.lost_have(0)

def test_rarer_in_started_takes_priority():
    p = PiecePicker(3)
    p.complete(2)
    p.requested(0)
    p.requested(1)
    p.got_have(1)
    p.got_have(0)
    p.got_have(0)
    assert _pull(p) == [1, 0]

def test_zero():
    assert _pull(PiecePicker(0)) == []

def _pull(pp):
    r = []
    def want(p, r = r):
        return p not in r
    while True:
        n = pp.next(want)
        if n is None:
            break
        r.append(n)
    return r
