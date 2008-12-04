# Written by Bram Cohen
# see LICENSE.txt for license information

from sha import sha
from threading import Event
from bitfield import Bitfield

def dummy_status(fractionDone = None, activity = None):
    pass

def dummy_data_flunked(size):
    pass

class StorageWrapper:
    def __init__(self, storage, request_size, hashes, 
            piece_size, finished, failed, 
            statusfunc = dummy_status, flag = Event(), check_hashes = True,
            data_flunked = dummy_data_flunked):
        self.storage = storage
        self.request_size = request_size
        self.hashes = hashes
        self.piece_size = piece_size
        self.data_flunked = data_flunked
        self.total_length = storage.get_total_length()
        self.amount_left = self.total_length
        if self.total_length <= piece_size * (len(hashes) - 1):
            raise ValueError, 'bad data from tracker - total too small'
        if self.total_length > piece_size * len(hashes):
            raise ValueError, 'bad data from tracker - total too big'
        self.finished = finished
        self.failed = failed
        self.numactive = [0] * len(hashes)
        self.inactive_requests = [1] * len(hashes)
        self.amount_inactive = self.total_length
        self.endgame = False
        self.have = Bitfield(len(hashes))
        self.waschecked = [check_hashes] * len(hashes)
        self.places = {}
        self.holes = []
        if len(hashes) == 0:
            finished()
            return
        targets = {}
        total = len(hashes)
        for i in xrange(len(hashes)):
            if not self._waspre(i):
                targets.setdefault(hashes[i], []).append(i)
                total -= 1
        numchecked = 0.0
        if total and check_hashes:
            statusfunc({"activity" : 'checking existing file', 
                "fractionDone" : 0})
        def markgot(piece, pos, self = self, check_hashes = check_hashes):
            self.places[piece] = pos
            self.have[piece] = True
            self.amount_left -= self._piecelen(piece)
            self.amount_inactive -= self._piecelen(piece)
            self.inactive_requests[piece] = None
            self.waschecked[piece] = check_hashes
        lastlen = self._piecelen(len(hashes) - 1)
        for i in xrange(len(hashes)):
            if not self._waspre(i):
                self.holes.append(i)
            elif not check_hashes:
                markgot(i, i)
            else:
                sh = sha(self.storage.read(piece_size * i, lastlen))
                sp = sh.digest()
                sh.update(self.storage.read(piece_size * i + lastlen, self._piecelen(i) - lastlen))
                s = sh.digest()
                if s == hashes[i]:
                    markgot(i, i)
                elif targets.get(s) and self._piecelen(i) == self._piecelen(targets[s][-1]):
                    markgot(targets[s].pop(), i)
                elif not self.have[len(hashes) - 1] and sp == hashes[-1] and (i == len(hashes) - 1 or not self._waspre(len(hashes) - 1)):
                    markgot(len(hashes) - 1, i)
                else:
                    self.places[i] = i
                if flag.isSet():
                    return
                numchecked += 1
                statusfunc({'fractionDone': 1 - float(self.amount_left) / self.total_length})
        if self.amount_left == 0:
            finished()

    def _waspre(self, piece):
        return self.storage.was_preallocated(piece * self.piece_size, self._piecelen(piece))

    def _piecelen(self, piece):
        if piece < len(self.hashes) - 1:
            return self.piece_size
        else:
            return self.total_length - piece * self.piece_size

    def get_amount_left(self):
        return self.amount_left

    def do_I_have_anything(self):
        return self.amount_left < self.total_length

    def _make_inactive(self, index):
        length = min(self.piece_size, self.total_length - self.piece_size * index)
        l = []
        x = 0
        while x + self.request_size < length:
            l.append((x, self.request_size))
            x += self.request_size
        l.append((x, length - x))
        self.inactive_requests[index] = l

    def is_endgame(self):
        return self.endgame

    def get_have_list(self):
        return self.have.tostring()

    def do_I_have(self, index):
        return self.have[index]

    def do_I_have_requests(self, index):
        return not not self.inactive_requests[index]

    def new_request(self, index):
        # returns (begin, length)
        if self.inactive_requests[index] == 1:
            self._make_inactive(index)
        self.numactive[index] += 1
        rs = self.inactive_requests[index]
        r = min(rs)
        rs.remove(r)
        self.amount_inactive -= r[1]
        if self.amount_inactive == 0:
            self.endgame = True
        return r

    def piece_came_in(self, index, begin, piece):
        try:
            return self._piece_came_in(index, begin, piece)
        except IOError, e:
            self.failed('IO Error ' + str(e))
            return True

    def _piece_came_in(self, index, begin, piece):
        if not self.places.has_key(index):
            n = self.holes.pop(0)
            if self.places.has_key(n):
                oldpos = self.places[n]
                old = self.storage.read(self.piece_size * oldpos, self._piecelen(n))
                if self.have[n] and sha(old).digest() != self.hashes[n]:
                    self.failed('data corrupted on disk - maybe you have two copies running?')
                    return True
                self.storage.write(self.piece_size * n, old)
                self.places[n] = n
                if index == oldpos or index in self.holes:
                    self.places[index] = oldpos
                else:
                    for p, v in self.places.items():
                        if v == index:
                            break
                    self.places[index] = index
                    self.places[p] = oldpos
                    old = self.storage.read(self.piece_size * index, self.piece_size)
                    self.storage.write(self.piece_size * oldpos, old)
            elif index in self.holes or index == n:
                if not self._waspre(n):
                    self.storage.write(self.piece_size * n, self._piecelen(n) * chr(0xFF))
                self.places[index] = n
            else:
                for p, v in self.places.items():
                    if v == index:
                        break
                self.places[index] = index
                self.places[p] = n
                old = self.storage.read(self.piece_size * index, self._piecelen(n))
                self.storage.write(self.piece_size * n, old)
        self.storage.write(self.places[index] * self.piece_size + begin, piece)
        self.numactive[index] -= 1
        if not self.inactive_requests[index] and not self.numactive[index]:
            if sha(self.storage.read(self.piece_size * self.places[index], self._piecelen(index))).digest() == self.hashes[index]:
                self.have[index] = True
                self.inactive_requests[index] = None
                self.waschecked[index] = True
                self.amount_left -= self._piecelen(index)
                if self.amount_left == 0:
                    self.finished()
            else:
                self.data_flunked(self._piecelen(index))
                self.inactive_requests[index] = 1
                self.amount_inactive += self._piecelen(index)
                return False
        return True

    def request_lost(self, index, begin, length):
        self.inactive_requests[index].append((begin, length))
        self.amount_inactive += length
        self.numactive[index] -= 1

    def get_piece(self, index, begin, length):
        try:
            return self._get_piece(index, begin, length)
        except IOError, e:
            self.failed('IO Error ' + str(e))
            return None

    def _get_piece(self, index, begin, length):
        if not self.have[index]:
            return None
        if not self.waschecked[index]:
            if sha(self.storage.read(self.piece_size * self.places[index], self._piecelen(index))).digest() != self.hashes[index]:
                self.failed('told file complete on start-up, but piece failed hash check')
                return None
            self.waschecked[index] = True
        if begin + length > self._piecelen(index):
            return None
        return self.storage.read(self.piece_size * self.places[index] + begin, length)

class DummyStorage:
    def __init__(self, total, pre = False, ranges = []):
        self.pre = pre
        self.ranges = ranges
        self.s = chr(0xFF) * total
        self.done = False

    def was_preexisting(self):
        return self.pre

    def was_preallocated(self, begin, length):
        for b, l in self.ranges:
            if begin >= b and begin + length <= b + l:
                return True
        return False

    def get_total_length(self):
        return len(self.s)

    def read(self, begin, length):
        return self.s[begin:begin + length]

    def write(self, begin, piece):
        self.s = self.s[:begin] + piece + self.s[begin + len(piece):]

    def finished(self):
        self.done = True

def test_basic():
    ds = DummyStorage(3)
    sw = StorageWrapper(ds, 2, [sha('abc').digest()], 4, ds.finished, None)
    assert sw.get_amount_left() == 3
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert sw.do_I_have_requests(0)
    x = []
    x.append(sw.new_request(0))
    assert sw.do_I_have_requests(0)
    x.append(sw.new_request(0))
    assert not sw.do_I_have_requests(0)
    x.sort()
    assert x == [(0, 2), (2, 1)]
    sw.request_lost(0, 2, 1)
    del x[-1]
    assert sw.do_I_have_requests(0)
    x.append(sw.new_request(0))
    assert x == [(0, 2), (2, 1)]
    assert not sw.do_I_have_requests(0)
    sw.piece_came_in(0, 0, 'ab')
    assert not sw.do_I_have_requests(0)
    assert sw.get_amount_left() == 3
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert not ds.done
    sw.piece_came_in(0, 2, 'c')
    assert not sw.do_I_have_requests(0)
    assert sw.get_amount_left() == 0
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0x80)
    assert sw.get_piece(0, 0, 3) == 'abc'
    assert sw.get_piece(0, 1, 2) == 'bc'
    assert sw.get_piece(0, 0, 2) == 'ab'
    assert sw.get_piece(0, 1, 1) == 'b'
    assert ds.done

def test_two_pieces():
    ds = DummyStorage(4)
    sw = StorageWrapper(ds, 3, [sha('abc').digest(),
        sha('d').digest()], 3, ds.finished, None)
    assert sw.get_amount_left() == 4
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert sw.do_I_have_requests(0)
    assert sw.do_I_have_requests(1)

    assert sw.new_request(0) == (0, 3)
    assert sw.get_amount_left() == 4
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert not sw.do_I_have_requests(0)
    assert sw.do_I_have_requests(1)

    assert sw.new_request(1) == (0, 1)
    assert sw.get_amount_left() == 4
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert not sw.do_I_have_requests(0)
    assert not sw.do_I_have_requests(1)

    sw.piece_came_in(0, 0, 'abc')
    assert sw.get_amount_left() == 1
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0x80)
    assert not sw.do_I_have_requests(0)
    assert not sw.do_I_have_requests(1)
    assert sw.get_piece(0, 0, 3) == 'abc'
    assert not ds.done

    sw.piece_came_in(1, 0, 'd')
    assert ds.done
    assert sw.get_amount_left() == 0
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0xC0)
    assert not sw.do_I_have_requests(0)
    assert not sw.do_I_have_requests(1)
    assert sw.get_piece(1, 0, 1) == 'd'

def test_hash_fail():
    ds = DummyStorage(4)
    sw = StorageWrapper(ds, 4, [sha('abcd').digest()], 4, ds.finished, None)
    assert sw.get_amount_left() == 4
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert sw.do_I_have_requests(0)

    assert sw.new_request(0) == (0, 4)
    sw.piece_came_in(0, 0, 'abcx')
    assert sw.get_amount_left() == 4
    assert not sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0)
    assert sw.do_I_have_requests(0)

    assert sw.new_request(0) == (0, 4)
    assert not ds.done
    sw.piece_came_in(0, 0, 'abcd')
    assert ds.done
    assert sw.get_amount_left() == 0
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0x80)
    assert not sw.do_I_have_requests(0)

def test_lazy_hashing():
    ds = DummyStorage(4, ranges = [(0, 4)])
    flag = Event()
    sw = StorageWrapper(ds, 4, [sha('abcd').digest()], 4, ds.finished, lambda x, flag = flag: flag.set(), check_hashes = False)
    assert sw.get_piece(0, 0, 2) is None
    assert flag.isSet()

def test_lazy_hashing_pass():
    ds = DummyStorage(4)
    flag = Event()
    sw = StorageWrapper(ds, 4, [sha(chr(0xFF) * 4).digest()], 4, ds.finished, lambda x, flag = flag: flag.set(), check_hashes = False)
    assert sw.get_piece(0, 0, 2) is None
    assert not flag.isSet()

def test_preexisting():
    ds = DummyStorage(4, True, [(0, 4)])
    sw = StorageWrapper(ds, 2, [sha(chr(0xFF) * 2).digest(), 
        sha('ab').digest()], 2, ds.finished, None)
    assert sw.get_amount_left() == 2
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0x80)
    assert not sw.do_I_have_requests(0)
    assert sw.do_I_have_requests(1)
    assert sw.new_request(1) == (0, 2)
    assert not ds.done
    sw.piece_came_in(1, 0, 'ab')
    assert ds.done
    assert sw.get_amount_left() == 0
    assert sw.do_I_have_anything()
    assert sw.get_have_list() == chr(0xC0)
    assert not sw.do_I_have_requests(0)
    assert not sw.do_I_have_requests(1)

def test_total_too_short():
    ds = DummyStorage(4)
    try:
        StorageWrapper(ds, 4, [sha(chr(0xff) * 4).digest(),
            sha(chr(0xFF) * 4).digest()], 4, ds.finished, None)
        raise 'fail'
    except ValueError:
        pass

def test_total_too_big():
    ds = DummyStorage(9)
    try:
        sw = StorageWrapper(ds, 4, [sha('qqqq').digest(),
            sha(chr(0xFF) * 4).digest()], 4, ds.finished, None)
        raise 'fail'
    except ValueError:
        pass

def test_end_above_total_length():
    ds = DummyStorage(3, True)
    sw = StorageWrapper(ds, 4, [sha('qqq').digest()], 4, ds.finished, None)
    assert sw.get_piece(0, 0, 4) == None

def test_end_past_piece_end():
    ds = DummyStorage(4, True, ranges = [(0, 4)])
    sw = StorageWrapper(ds, 4, [sha(chr(0xFF) * 2).digest(), 
        sha(chr(0xFF) * 2).digest()], 2, ds.finished, None)
    assert ds.done
    assert sw.get_piece(0, 0, 3) == None

from random import shuffle

def test_alloc_random():
    ds = DummyStorage(101)
    sw = StorageWrapper(ds, 1, [sha(chr(i)).digest() for i in xrange(101)], 1, ds.finished, None)
    for i in xrange(100):
        assert sw.new_request(i) == (0, 1)
    r = range(100)
    shuffle(r)
    for i in r:
        sw.piece_came_in(i, 0, chr(i))
    for i in xrange(100):
        assert sw.get_piece(i, 0, 1) == chr(i)
    assert ds.s[:100] == ''.join([chr(i) for i in xrange(100)])

def test_alloc_resume():
    ds = DummyStorage(101)
    sw = StorageWrapper(ds, 1, [sha(chr(i)).digest() for i in xrange(101)], 1, ds.finished, None)
    for i in xrange(100):
        assert sw.new_request(i) == (0, 1)
    r = range(100)
    shuffle(r)
    for i in r[:50]:
        sw.piece_came_in(i, 0, chr(i))
    assert ds.s[50:] == chr(0xFF) * 51
    ds.ranges = [(0, 50)]
    sw = StorageWrapper(ds, 1, [sha(chr(i)).digest() for i in xrange(101)], 1, ds.finished, None)
    for i in r[50:]:
        sw.piece_came_in(i, 0, chr(i))
    assert ds.s[:100] == ''.join([chr(i) for i in xrange(100)])

def test_last_piece_pre():
    ds = DummyStorage(3, ranges = [(2, 1)])
    ds.s = chr(0xFF) + chr(0xFF) + 'c'
    sw = StorageWrapper(ds, 2, [sha('ab').digest(), sha('c').digest()], 2, ds.finished, None)
    assert not sw.do_I_have_requests(1)
    assert sw.do_I_have_requests(0)

def test_not_last_pre():
    ds = DummyStorage(3, ranges = [(1, 1)])
    ds.s = chr(0xFF) + 'a' + chr(0xFF)
    sw = StorageWrapper(ds, 1, [sha('a').digest()] * 3, 1, ds.finished, None)
    assert not sw.do_I_have_requests(1)
    assert sw.do_I_have_requests(0)
    assert sw.do_I_have_requests(2)

def test_last_piece_not_pre():
    ds = DummyStorage(51, ranges = [(50, 1)])
    sw = StorageWrapper(ds, 2, [sha('aa').digest()] * 25 + [sha('b').digest()], 2, ds.finished, None)
    for i in xrange(25):
        assert sw.new_request(i) == (0, 2)
    assert sw.new_request(25) == (0, 1)
    sw.piece_came_in(25, 0, 'b')
    r = range(25)
    shuffle(r)
    for i in r:
        sw.piece_came_in(i, 0, 'aa')
    assert ds.done
    assert ds.s == 'a' * 50 + 'b'
