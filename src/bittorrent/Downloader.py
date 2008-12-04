# Written by Bram Cohen
# see LICENSE.txt for license information

from CurrentRateMeasure import Measure
from random import shuffle
from time import time
from bitfield import Bitfield

class SingleDownload:
    def __init__(self, downloader, connection):
        self.downloader = downloader
        self.connection = connection
        self.choked = True
        self.interested = False
        self.active_requests = []
        self.measure = Measure(downloader.max_rate_period)
        self.have = Bitfield(downloader.numpieces)
        self.last = 0
        self.example_interest = None

    def disconnected(self):
        self.downloader.downloads.remove(self)
        for i in xrange(len(self.have)):
            if self.have[i]:
                self.downloader.picker.lost_have(i)
        self._letgo()

    def _letgo(self):
        if not self.active_requests:
            return
        if self.downloader.storage.is_endgame():
            self.active_requests = []
            return
        lost = []
        for index, begin, length in self.active_requests:
            self.downloader.storage.request_lost(index, begin, length)
            if index not in lost:
                lost.append(index)
        self.active_requests = []
        ds = [d for d in self.downloader.downloads if not d.choked]
        shuffle(ds)
        for d in ds:
            d._request_more(lost)
        for d in self.downloader.downloads:
            if d.choked and not d.interested:
                for l in lost:
                    if d.have[l] and self.downloader.storage.do_I_have_requests(l):
                        d.interested = True
                        d.connection.send_interested()
                        break

    def got_choke(self):
        if not self.choked:
            self.choked = True
            self._letgo()

    def got_unchoke(self):
        if self.choked:
            self.choked = False
            if self.interested:
                self._request_more()

    def is_choked(self):
        return self.choked

    def is_interested(self):
        return self.interested

    def got_piece(self, index, begin, piece):
        try:
            self.active_requests.remove((index, begin, len(piece)))
        except ValueError:
            return False
        if self.downloader.storage.is_endgame():
            self.downloader.all_requests.remove((index, begin, len(piece)))
        self.last = time()
        self.measure.update_rate(len(piece))
        self.downloader.measurefunc(len(piece))
        self.downloader.downmeasure.update_rate(len(piece))
        if not self.downloader.storage.piece_came_in(index, begin, piece):
            if self.downloader.storage.is_endgame():
                while self.downloader.storage.do_I_have_requests(index):
                    nb, nl = self.downloader.storage.new_request(index)
                    self.downloader.all_requests.append((index, nb, nl))
                for d in self.downloader.downloads:
                    d.fix_download_endgame()
                return False
            self.downloader.picker.bump(index)
            ds = [d for d in self.downloader.downloads if not d.choked]
            shuffle(ds)
            for d in ds:
                d._request_more([index])
            return False
        if self.downloader.storage.do_I_have(index):
            self.downloader.picker.complete(index)
        if self.downloader.storage.is_endgame():
            for d in self.downloader.downloads:
                if d is not self and d.interested:
                    if d.choked:
                        d.fix_download_endgame()
                    else:
                        try:
                            d.active_requests.remove((index, begin, len(piece)))
                        except ValueError:
                            continue
                        d.connection.send_cancel(index, begin, len(piece))
                        d.fix_download_endgame()
        self._request_more()
        if self.downloader.picker.am_I_complete():
            for d in [i for i in self.downloader.downloads if i.have.numfalse == 0]:
                d.connection.close()
        return self.downloader.storage.do_I_have(index)

    def _want(self, index):
        return self.have[index] and self.downloader.storage.do_I_have_requests(index)

    def _request_more(self, indices = None):
        assert not self.choked
        if len(self.active_requests) == self.downloader.backlog:
            return
        if self.downloader.storage.is_endgame():
            self.fix_download_endgame()
            return
        lost_interests = []
        while len(self.active_requests) < self.downloader.backlog:
            if indices is None:
                interest = self.downloader.picker.next(self._want, self.have.numfalse == 0)
            else:
                interest = None
                for i in indices:
                    if self.have[i] and self.downloader.storage.do_I_have_requests(i):
                        interest = i
                        break
            if interest is None:
                break
            if not self.interested:
                self.interested = True
                self.connection.send_interested()
            self.example_interest = interest
            begin, length = self.downloader.storage.new_request(interest)
            self.downloader.picker.requested(interest, self.have.numfalse == 0)
            self.active_requests.append((interest, begin, length))
            self.connection.send_request(interest, begin, length)
            if not self.downloader.storage.do_I_have_requests(interest):
                lost_interests.append(interest)
        if not self.active_requests and self.interested:
            self.interested = False
            self.connection.send_not_interested()
        if lost_interests:
            for d in self.downloader.downloads:
                if d.active_requests or not d.interested:
                    continue
                if d.example_interest is not None and self.downloader.storage.do_I_have_requests(d.example_interest):
                    continue
                for lost in lost_interests:
                    if d.have[lost]:
                        break
                else:
                    continue
                interest = self.downloader.picker.next(d._want, d.have.numfalse == 0)
                if interest is None:
                    d.interested = False
                    d.connection.send_not_interested()
                else:
                    d.example_interest = interest
        if self.downloader.storage.is_endgame():
            self.downloader.all_requests = []
            for d in self.downloader.downloads:
                self.downloader.all_requests.extend(d.active_requests)
            for d in self.downloader.downloads:
                d.fix_download_endgame()

    def fix_download_endgame(self):
        want = [a for a in self.downloader.all_requests if self.have[a[0]] and a not in self.active_requests]
        if self.interested and not self.active_requests and not want:
            self.interested = False
            self.connection.send_not_interested()
            return
        if not self.interested and want:
            self.interested = True
            self.connection.send_interested()
        if self.choked:
            return
        shuffle(want)
        del want[self.downloader.backlog - len(self.active_requests):]
        self.active_requests.extend(want)
        for piece, begin, length in want:
            self.connection.send_request(piece, begin, length)

    def got_have(self, index):
        if self.have[index]:
            return
        self.have[index] = True
        self.downloader.picker.got_have(index)
        if self.downloader.picker.am_I_complete() and self.have.numfalse == 0:
            self.connection.close()
            return
        if self.downloader.storage.is_endgame():
            self.fix_download_endgame()
        elif self.downloader.storage.do_I_have_requests(index):
            if not self.choked:
                self._request_more([index])
            else:
                if not self.interested:
                    self.interested = True
                    self.connection.send_interested()

    def got_have_bitfield(self, have):
        self.have = have
        for i in xrange(len(self.have)):
            if self.have[i]:
                self.downloader.picker.got_have(i)
        if self.downloader.picker.am_I_complete() and self.have.numfalse == 0:
            self.connection.close()
            return
        if self.downloader.storage.is_endgame():
            for piece, begin, length in self.downloader.all_requests:
                if self.have[piece]:
                    self.interested = True
                    self.connection.send_interested()
                    return
        for i in xrange(len(self.have)):
            if self.have[i] and self.downloader.storage.do_I_have_requests(i):
                self.interested = True
                self.connection.send_interested()
                return

    def get_rate(self):
        return self.measure.get_rate()

    def is_snubbed(self):
        return time() - self.last > self.downloader.snub_time

class Downloader:
    def __init__(self, storage, picker, backlog, max_rate_period, numpieces, 
            downmeasure, snub_time, measurefunc = lambda x: None):
        self.storage = storage
        self.picker = picker
        self.backlog = backlog
        self.max_rate_period = max_rate_period
        self.downmeasure = downmeasure
        self.numpieces = numpieces
        self.snub_time = snub_time
        self.measurefunc = measurefunc
        self.downloads = []

    def make_download(self, connection):
        self.downloads.append(SingleDownload(self, connection))
        return self.downloads[-1]

class DummyPicker:
    def __init__(self, num, r):
        self.stuff = range(num)
        self.r = r

    def next(self, wantfunc, seed):
        for i in self.stuff:
            if wantfunc(i):
                return i
        return None

    def lost_have(self, pos):
        self.r.append('lost have')

    def got_have(self, pos):
        self.r.append('got have')

    def requested(self, pos, seed):
        self.r.append('requested')

    def complete(self, pos):
        self.stuff.remove(pos)
        self.r.append('complete')

    def am_I_complete(self):
        return False

    def bump(self, i):
        pass

class DummyStorage:
    def __init__(self, remaining, have_endgame = False, numpieces = 1):
        self.remaining = remaining
        self.active = [[] for i in xrange(numpieces)]
        self.endgame = False
        self.have_endgame = have_endgame

    def do_I_have_requests(self, index):
        return self.remaining[index] != []
        
    def request_lost(self, index, begin, length):
        x = (begin, length)
        self.active[index].remove(x)
        self.remaining[index].append(x)
        self.remaining[index].sort()
        
    def piece_came_in(self, index, begin, piece):
        self.active[index].remove((begin, len(piece)))
        return True
        
    def do_I_have(self, index):
        return (self.remaining[index] == [] and 
            self.active[index] == [])
        
    def new_request(self, index):
        x = self.remaining[index].pop()
        for i in self.remaining:
            if i:
                break
        else:
            self.endgame = True
        self.active[index].append(x)
        self.active[index].sort()
        return x

    def is_endgame(self):
        return self.have_endgame and self.endgame

class DummyConnection:
    def __init__(self, events):
        self.events = events

    def send_interested(self):
        self.events.append('interested')
        
    def send_not_interested(self):
        self.events.append('not interested')
        
    def send_request(self, index, begin, length):
        self.events.append(('request', index, begin, length))

    def send_cancel(self, index, begin, length):
        self.events.append(('cancel', index, begin, length))

def test_stops_at_backlog():
    ds = DummyStorage([[(0, 2), (2, 2), (4, 2), (6, 2)]])
    events = []
    d = Downloader(ds, DummyPicker(len(ds.remaining), events), 2, 15, 1, Measure(15), 10)
    sd = d.make_download(DummyConnection(events))
    assert events == []
    assert ds.remaining == [[(0, 2), (2, 2), (4, 2), (6, 2)]]
    assert ds.active == [[]]
    sd.got_have_bitfield(Bitfield(1, chr(0x80)))
    assert events == ['got have', 'interested']
    del events[:]
    assert ds.remaining == [[(0, 2), (2, 2), (4, 2), (6, 2)]]
    assert ds.active == [[]]
    sd.got_unchoke()
    assert events == ['requested', ('request', 0, 6, 2), 'requested', ('request', 0, 4, 2)]
    del events[:]
    assert ds.remaining == [[(0, 2), (2, 2)]]
    assert ds.active == [[(4, 2), (6, 2)]]
    sd.got_piece(0, 4, 'ab')
    assert events == ['requested', ('request', 0, 2, 2)]
    del events[:]
    assert ds.remaining == [[(0, 2)]]
    assert ds.active == [[(2, 2), (6, 2)]]

def test_got_have_single():
    ds = DummyStorage([[(0, 2)]])
    events = []
    d = Downloader(ds, DummyPicker(len(ds.remaining), events), 2, 15, 1, Measure(15), 10)
    sd = d.make_download(DummyConnection(events))
    assert events == []
    assert ds.remaining == [[(0, 2)]]
    assert ds.active == [[]]
    sd.got_unchoke()
    assert events == []
    assert ds.remaining == [[(0, 2)]]
    assert ds.active == [[]]
    sd.got_have(0)
    assert events == ['got have', 'interested', 'requested', ('request', 0, 0, 2)]
    del events[:]
    assert ds.remaining == [[]]
    assert ds.active == [[(0, 2)]]
    sd.disconnected()
    assert events == ['lost have']

def test_choke_clears_active():
    ds = DummyStorage([[(0, 2)]])
    events = []
    d = Downloader(ds, DummyPicker(len(ds.remaining), events), 2, 15, 1, Measure(15), 10)
    sd1 = d.make_download(DummyConnection(events))
    sd2 = d.make_download(DummyConnection(events))
    assert events == []
    assert ds.remaining == [[(0, 2)]]
    assert ds.active == [[]]
    sd1.got_unchoke()
    sd1.got_have(0)
    assert events == ['got have', 'interested', 'requested', ('request', 0, 0, 2)]
    del events[:]
    assert ds.remaining == [[]]
    assert ds.active == [[(0, 2)]]
    sd2.got_unchoke()
    sd2.got_have(0)
    assert events == ['got have']
    del events[:]
    assert ds.remaining == [[]]
    assert ds.active == [[(0, 2)]]
    sd1.got_choke()
    assert events == ['interested', 'requested', ('request', 0, 0, 2), 'not interested']
    del events[:]
    assert ds.remaining == [[]]
    assert ds.active == [[(0, 2)]]
    sd2.got_piece(0, 0, 'ab')
    assert events == ['complete', 'not interested']
    del events[:]
    assert ds.remaining == [[]]
    assert ds.active == [[]]

def test_endgame():
    ds = DummyStorage([[(0, 2)], [(0, 2)], [(0, 2)]], True, 3)
    events = []
    d = Downloader(ds, DummyPicker(len(ds.remaining), events), 10, 15, 3, Measure(15), 10)
    ev1 = []
    ev2 = []
    ev3 = []
    ev4 = []
    sd1 = d.make_download(DummyConnection(ev1))
    sd2 = d.make_download(DummyConnection(ev2))
    sd3 = d.make_download(DummyConnection(ev3))
    sd1.got_unchoke()
    sd1.got_have(0)
    assert ev1 == ['interested', ('request', 0, 0, 2)]
    del ev1[:]
    
    sd2.got_unchoke()
    sd2.got_have(0)
    sd2.got_have(1)
    assert ev2 == ['interested', ('request', 1, 0, 2)]
    del ev2[:]
    
    sd3.got_unchoke()
    sd3.got_have(0)
    sd3.got_have(1)
    sd3.got_have(2)
    assert (ev3 == ['interested', ('request', 2, 0, 2), ('request', 0, 0, 2), ('request', 1, 0, 2)] or 
        ev3 == ['interested', ('request', 2, 0, 2), ('request', 1, 0, 2), ('request', 0, 0, 2)])
    del ev3[:]
    assert ev2 == [('request', 0, 0, 2)]
    del ev2[:]

    sd2.got_piece(0, 0, 'ab')
    assert ev1 == [('cancel', 0, 0, 2), 'not interested']
    del ev1[:]
    assert ev2 == []
    assert ev3 == [('cancel', 0, 0, 2)]
    del ev3[:]

    sd3.got_choke()
    assert ev1 == []
    assert ev2 == []
    assert ev3 == []

    sd3.got_unchoke()
    assert (ev3 == [('request', 2, 0, 2), ('request', 1, 0, 2)] or 
        ev3 == [('request', 1, 0, 2), ('request', 2, 0, 2)])
    del ev3[:]
    assert ev1 == []
    assert ev2 == []

    sd4 = d.make_download(DummyConnection(ev4))
    sd4.got_have_bitfield([True, True, True])
    assert ev4 == ['interested']
    del ev4[:]
    sd4.got_unchoke()
    assert (ev4 == [('request', 2, 0, 2), ('request', 1, 0, 2)] or 
        ev4 == [('request', 1, 0, 2), ('request', 2, 0, 2)])
    assert ev1 == []
    assert ev2 == []
    assert ev3 == []

def test_stops_at_backlog_endgame():
    ds = DummyStorage([[(2, 2), (0, 2)], [(2, 2), (0, 2)], [(0, 2)]], True, 3)
    events = []
    d = Downloader(ds, DummyPicker(len(ds.remaining), events), 3, 15, 3, Measure(15), 10)
    ev1 = []
    ev2 = []
    ev3 = []
    sd1 = d.make_download(DummyConnection(ev1))
    sd2 = d.make_download(DummyConnection(ev2))
    sd3 = d.make_download(DummyConnection(ev3))

    sd1.got_unchoke()
    sd1.got_have(0)
    assert ev1 == ['interested', ('request', 0, 0, 2), ('request', 0, 2, 2)]
    del ev1[:]

    sd2.got_unchoke()
    sd2.got_have(0)
    assert ev2 == []
    sd2.got_have(1)
    assert ev2 == ['interested', ('request', 1, 0, 2), ('request', 1, 2, 2)]
    del ev2[:]

    sd3.got_unchoke()
    sd3.got_have(2)
    assert (ev2 == [('request', 0, 0, 2)] or 
        ev2 == [('request', 0, 2, 2)])
    n = ev2[0][2]
    del ev2[:]

    sd1.got_piece(0, n, 'ab')
    assert ev1 == []
    assert ev2 == [('cancel', 0, n, 2), ('request', 0, 2-n, 2)]
