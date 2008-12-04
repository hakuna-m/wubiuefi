# Written by Bram Cohen
# see LICENSE.txt for license information

from random import randrange

class Choker:
    def __init__(self, max_uploads, schedule, done = lambda: False, min_uploads = None):
        self.max_uploads = max_uploads
        if min_uploads is None:
            min_uploads = max_uploads
        self.min_uploads = min_uploads
        self.schedule = schedule
        self.connections = []
        self.count = 0
        self.done = done
        schedule(self._round_robin, 10)
    
    def _round_robin(self):
        self.schedule(self._round_robin, 10)
        self.count += 1
        if self.count % 3 == 0:
            for i in xrange(len(self.connections)):
                u = self.connections[i].get_upload()
                if u.is_choked() and u.is_interested():
                    self.connections = self.connections[i:] + self.connections[:i]
                    break
        self._rechoke()

    def _snubbed(self, c):
        if self.done():
            return False
        return c.get_download().is_snubbed()

    def _rate(self, c):
        if self.done():
            return c.get_upload().get_rate()
        else:
            return c.get_download().get_rate()

    def _rechoke(self):
        preferred = []
        for c in self.connections:
            if not self._snubbed(c) and c.get_upload().is_interested():
                preferred.append((-self._rate(c), c))
        preferred.sort()
        del preferred[self.max_uploads - 1:]
        preferred = [x[1] for x in preferred]
        count = len(preferred)
        hit = False
        for c in self.connections:
            u = c.get_upload()
            if c in preferred:
                u.unchoke()
            else:
                if count < self.min_uploads or not hit:
                    u.unchoke()
                    if u.is_interested():
                        count += 1
                        hit = True
                else:
                    u.choke()

    def connection_made(self, connection, p = None):
        if p is None:
            p = randrange(-2, len(self.connections) + 1)
        self.connections.insert(max(p, 0), connection)
        self._rechoke()

    def connection_lost(self, connection):
        self.connections.remove(connection)
        if connection.get_upload().is_interested() and not connection.get_upload().is_choked():
            self._rechoke()

    def interested(self, connection):
        if not connection.get_upload().is_choked():
            self._rechoke()

    def not_interested(self, connection):
        if not connection.get_upload().is_choked():
            self._rechoke()

    def change_max_uploads(self, newval):
        def foo(self=self, newval=newval):
            self._change_max_uploads(newval)
        self.schedule(foo, 0);
        
    def _change_max_uploads(self, newval):
        self.max_uploads = newval
        self._rechoke()

class DummyScheduler:
    def __init__(self):
        self.s = []

    def __call__(self, func, delay):
        self.s.append((func, delay))

class DummyConnection:
    def __init__(self, v = 0):
        self.u = DummyUploader()
        self.d = DummyDownloader(self)
        self.v = v
    
    def get_upload(self):
        return self.u

    def get_download(self):
        return self.d

class DummyDownloader:
    def __init__(self, c):
        self.s = False
        self.c = c

    def is_snubbed(self):
        return self.s

    def get_rate(self):
        return self.c.v

class DummyUploader:
    def __init__(self):
        self.i = False
        self.c = True

    def choke(self):
        if not self.c:
            self.c = True

    def unchoke(self):
        if self.c:
            self.c = False

    def is_choked(self):
        return self.c

    def is_interested(self):
        return self.i

def test_round_robin_with_no_downloads():
    s = DummyScheduler()
    Choker(2, s)
    assert len(s.s) == 1
    assert s.s[0][1] == 10
    s.s[0][0]()
    del s.s[0]
    assert len(s.s) == 1
    assert s.s[0][1] == 10
    s.s[0][0]()
    del s.s[0]
    s.s[0][0]()
    del s.s[0]
    s.s[0][0]()
    del s.s[0]

def test_resort():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection()
    c2 = DummyConnection(1)
    c3 = DummyConnection(2)
    c4 = DummyConnection(3)
    c2.u.i = True
    c3.u.i = True
    choker.connection_made(c1)
    assert not c1.u.c
    choker.connection_made(c2, 1)
    assert not c1.u.c
    assert not c2.u.c
    choker.connection_made(c3, 1)
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c
    c2.v = 2
    c3.v = 1
    choker.connection_made(c4, 1)
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c
    assert not c4.u.c
    choker.connection_lost(c4)
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c
    s.s[0][0]()
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c

def test_interest():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection()
    c2 = DummyConnection(1)
    c3 = DummyConnection(2)
    c2.u.i = True
    c3.u.i = True
    choker.connection_made(c1)
    assert not c1.u.c
    choker.connection_made(c2, 1)
    assert not c1.u.c
    assert not c2.u.c
    choker.connection_made(c3, 1)
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c
    c3.u.i = False
    choker.not_interested(c3)
    assert not c1.u.c
    assert not c2.u.c
    assert not c3.u.c
    c3.u.i = True
    choker.interested(c3)
    assert not c1.u.c
    assert c2.u.c
    assert not c3.u.c
    choker.connection_lost(c3)
    assert not c1.u.c
    assert not c2.u.c

def test_robin_interest():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(1)
    c1.u.i = True
    choker.connection_made(c2)
    assert not c2.u.c
    choker.connection_made(c1, 0)
    assert not c1.u.c
    assert c2.u.c
    c1.u.i = False
    choker.not_interested(c1)
    assert not c1.u.c
    assert not c2.u.c
    c1.u.i = True
    choker.interested(c1)
    assert not c1.u.c
    assert c2.u.c
    choker.connection_lost(c1)
    assert not c2.u.c

def test_skip_not_interested():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(1)
    c3 = DummyConnection(2)
    c1.u.i = True
    c3.u.i = True
    choker.connection_made(c2)
    assert not c2.u.c
    choker.connection_made(c1, 0)
    assert not c1.u.c
    assert c2.u.c
    choker.connection_made(c3, 2)
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f = s.s[0][0]
    f()
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f()
    assert c1.u.c
    assert c2.u.c
    assert not c3.u.c

def test_connection_lost_no_interrupt():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(1)
    c3 = DummyConnection(2)
    c1.u.i = True
    c2.u.i = True
    c3.u.i = True
    choker.connection_made(c1)
    choker.connection_made(c2, 1)
    choker.connection_made(c3, 2)
    f = s.s[0][0]
    f()
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    assert c3.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    assert c3.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    assert c3.u.c
    choker.connection_lost(c3)
    assert c1.u.c
    assert not c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    choker.connection_lost(c2)
    assert not c1.u.c

def test_connection_made_no_interrupt():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(1)
    c3 = DummyConnection(2)
    c1.u.i = True
    c2.u.i = True
    c3.u.i = True
    choker.connection_made(c1)
    choker.connection_made(c2, 1)
    f = s.s[0][0]
    assert not c1.u.c
    assert c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    choker.connection_made(c3, 1)
    assert not c1.u.c
    assert c2.u.c
    assert c3.u.c
    f()
    assert c1.u.c
    assert c2.u.c
    assert not c3.u.c

def test_round_robin():
    s = DummyScheduler()
    choker = Choker(1, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(1)
    c1.u.i = True
    c2.u.i = True
    choker.connection_made(c1)
    choker.connection_made(c2, 1)
    f = s.s[0][0]
    assert not c1.u.c
    assert c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    f()
    assert c1.u.c
    assert not c2.u.c
    f()
    assert not c1.u.c
    assert c2.u.c
    
def test_multi():
    s = DummyScheduler()
    choker = Choker(4, s)
    c1 = DummyConnection(0)
    c2 = DummyConnection(0)
    c3 = DummyConnection(0)
    c4 = DummyConnection(8)
    c5 = DummyConnection(0)
    c6 = DummyConnection(0)
    c7 = DummyConnection(6)
    c8 = DummyConnection(0)
    c9 = DummyConnection(9)
    c10 = DummyConnection(7)
    c11 = DummyConnection(10)
    choker.connection_made(c1, 0)
    choker.connection_made(c2, 1)
    choker.connection_made(c3, 2)
    choker.connection_made(c4, 3)
    choker.connection_made(c5, 4)
    choker.connection_made(c6, 5)
    choker.connection_made(c7, 6)
    choker.connection_made(c8, 7)
    choker.connection_made(c9, 8)
    choker.connection_made(c10, 9)
    choker.connection_made(c11, 10)
    c2.u.i = True
    c4.u.i = True
    c6.u.i = True
    c8.u.i = True
    c10.u.i = True
    c2.d.s = True
    c6.d.s = True
    c8.d.s = True
    s.s[0][0]()
    assert not c1.u.c
    assert not c2.u.c
    assert not c3.u.c
    assert not c4.u.c
    assert not c5.u.c
    assert not c6.u.c
    assert c7.u.c
    assert c8.u.c
    assert c9.u.c
    assert not c10.u.c
    assert c11.u.c


