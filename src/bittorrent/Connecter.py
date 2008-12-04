# Written by Bram Cohen
# see LICENSE.txt for license information

from bitfield import Bitfield
from binascii import b2a_hex
from CurrentRateMeasure import Measure

def toint(s):
    return long(b2a_hex(s), 16)

def tobinary(i):
    return (chr(i >> 24) + chr((i >> 16) & 0xFF) + 
        chr((i >> 8) & 0xFF) + chr(i & 0xFF))

CHOKE = chr(0)
UNCHOKE = chr(1)
INTERESTED = chr(2)
NOT_INTERESTED = chr(3)
# index
HAVE = chr(4)
# index, bitfield
BITFIELD = chr(5)
# index, begin, length
REQUEST = chr(6)
# index, begin, piece
PIECE = chr(7)
# index, begin, piece
CANCEL = chr(8)

class Connection:
    def __init__(self, connection, connecter):
        self.connection = connection
        self.connecter = connecter
        self.got_anything = False

    def get_ip(self):
        return self.connection.get_ip()

    def get_id(self):
        return self.connection.get_id()

    def close(self):
        self.connection.close()

    def is_flushed(self):
        if self.connecter.rate_capped:
            return False
        return self.connection.is_flushed()

    def is_locally_initiated(self):
        return self.connection.is_locally_initiated()

    def send_interested(self):
        self.connection.send_message(INTERESTED)

    def send_not_interested(self):
        self.connection.send_message(NOT_INTERESTED)

    def send_choke(self):
        self.connection.send_message(CHOKE)

    def send_unchoke(self):
        self.connection.send_message(UNCHOKE)

    def send_request(self, index, begin, length):
        self.connection.send_message(REQUEST + tobinary(index) + 
            tobinary(begin) + tobinary(length))

    def send_cancel(self, index, begin, length):
        self.connection.send_message(CANCEL + tobinary(index) + 
            tobinary(begin) + tobinary(length))

    def send_piece(self, index, begin, piece):
        assert not self.connecter.rate_capped
        self.connecter._update_upload_rate(len(piece))
        self.connection.send_message(PIECE + tobinary(index) + 
            tobinary(begin) + piece)

    def send_bitfield(self, bitfield):
        self.connection.send_message(BITFIELD + bitfield)

    def send_have(self, index):
        self.connection.send_message(HAVE + tobinary(index))

    def get_upload(self):
        return self.upload

    def get_download(self):
        return self.download

class Connecter:
    def __init__(self, make_upload, downloader, choker, numpieces,
            totalup, max_upload_rate = 0, sched = None):
        self.downloader = downloader
        self.make_upload = make_upload
        self.choker = choker
        self.numpieces = numpieces
        self.max_upload_rate = max_upload_rate
        self.sched = sched
        self.totalup = totalup
        self.rate_capped = False
        self.connections = {}

    def _update_upload_rate(self, amount):
        self.totalup.update_rate(amount)
        if self.max_upload_rate > 0 and self.totalup.get_rate_noupdate() > self.max_upload_rate:
            self.rate_capped = True
            self.sched(self._uncap, self.totalup.time_until_rate(self.max_upload_rate))

    def _uncap(self):
        self.rate_capped = False
        while not self.rate_capped:
            up = None
            minrate = None
            for i in self.connections.values():
                if not i.upload.is_choked() and i.upload.has_queries() and i.connection.is_flushed():
                    rate = i.upload.get_rate()
                    if up is None or rate < minrate:
                        up = i.upload
                        minrate = rate
            if up is None:
                break
            up.flushed()
            if self.totalup.get_rate_noupdate() > self.max_upload_rate:
                break

    def change_max_upload_rate(self, newval):
        def foo(self=self, newval=newval):
            self._change_max_upload_rate(newval)
        self.sched(foo, 0);
        
    def _change_max_upload_rate(self, newval):
        self.max_upload_rate = newval
        self._uncap()
        
    def how_many_connections(self):
        return len(self.connections)

    def connection_made(self, connection):
        c = Connection(connection, self)
        self.connections[connection] = c
        c.upload = self.make_upload(c)
        c.download = self.downloader.make_download(c)
        self.choker.connection_made(c)

    def connection_lost(self, connection):
        c = self.connections[connection]
        d = c.download
        del self.connections[connection]
        d.disconnected()
        self.choker.connection_lost(c)

    def connection_flushed(self, connection):
        self.connections[connection].upload.flushed()

    def got_message(self, connection, message):
        c = self.connections[connection]
        t = message[0]
        if t == BITFIELD and c.got_anything:
            connection.close()
            return
        c.got_anything = True
        if (t in [CHOKE, UNCHOKE, INTERESTED, NOT_INTERESTED] and 
                len(message) != 1):
            connection.close()
            return
        if t == CHOKE:
            c.download.got_choke()
        elif t == UNCHOKE:
            c.download.got_unchoke()
        elif t == INTERESTED:
            c.upload.got_interested()
        elif t == NOT_INTERESTED:
            c.upload.got_not_interested()
        elif t == HAVE:
            if len(message) != 5:
                connection.close()
                return
            i = toint(message[1:])
            if i >= self.numpieces:
                connection.close()
                return
            c.download.got_have(i)
        elif t == BITFIELD:
            try:
                b = Bitfield(self.numpieces, message[1:])
            except ValueError:
                connection.close()
                return
            c.download.got_have_bitfield(b)
        elif t == REQUEST:
            if len(message) != 13:
                connection.close()
                return
            i = toint(message[1:5])
            if i >= self.numpieces:
                connection.close()
                return
            c.upload.got_request(i, toint(message[5:9]), 
                toint(message[9:]))
        elif t == CANCEL:
            if len(message) != 13:
                connection.close()
                return
            i = toint(message[1:5])
            if i >= self.numpieces:
                connection.close()
                return
            c.upload.got_cancel(i, toint(message[5:9]), 
                toint(message[9:]))
        elif t == PIECE:
            if len(message) <= 9:
                connection.close()
                return
            i = toint(message[1:5])
            if i >= self.numpieces:
                connection.close()
                return
            if c.download.got_piece(i, toint(message[5:9]), message[9:]):
                for co in self.connections.values():
                    co.send_have(i)
        else:
            connection.close()

class DummyUpload:
    def __init__(self, events):
        self.events = events
        events.append('made upload')

    def flushed(self):
        self.events.append('flushed')

    def got_interested(self):
        self.events.append('interested')
        
    def got_not_interested(self):
        self.events.append('not interested')

    def got_request(self, index, begin, length):
        self.events.append(('request', index, begin, length))

    def got_cancel(self, index, begin, length):
        self.events.append(('cancel', index, begin, length))

class DummyDownload:
    def __init__(self, events):
        self.events = events
        events.append('made download')
        self.hit = 0

    def disconnected(self):
        self.events.append('disconnected')

    def got_choke(self):
        self.events.append('choke')

    def got_unchoke(self):
        self.events.append('unchoke')

    def got_have(self, i):
        self.events.append(('have', i))

    def got_have_bitfield(self, bitfield):
        self.events.append(('bitfield', bitfield.tostring()))

    def got_piece(self, index, begin, piece):
        self.events.append(('piece', index, begin, piece))
        self.hit += 1
        return self.hit > 1

class DummyDownloader:
    def __init__(self, events):
        self.events = events

    def make_download(self, connection):
        return DummyDownload(self.events)

class DummyConnection:
    def __init__(self, events):
        self.events = events

    def send_message(self, message):
        self.events.append(('m', message))

class DummyChoker:
    def __init__(self, events, cs):
        self.events = events
        self.cs = cs

    def connection_made(self, c):
        self.events.append('made')
        self.cs.append(c)

    def connection_lost(self, c):
        self.events.append('lost')

def test_operation():
    events = []
    cs = []
    co = Connecter(lambda c, events = events: DummyUpload(events), 
        DummyDownloader(events), DummyChoker(events, cs), 3, 
        Measure(10))
    assert events == []
    assert cs == []
    
    dc = DummyConnection(events)
    co.connection_made(dc)
    assert len(cs) == 1
    cc = cs[0]
    co.got_message(dc, BITFIELD + chr(0xc0))
    co.got_message(dc, CHOKE)
    co.got_message(dc, UNCHOKE)
    co.got_message(dc, INTERESTED)
    co.got_message(dc, NOT_INTERESTED)
    co.got_message(dc, HAVE + tobinary(2))
    co.got_message(dc, REQUEST + tobinary(1) + tobinary(5) + tobinary(6))
    co.got_message(dc, CANCEL + tobinary(2) + tobinary(3) + tobinary(4))
    co.got_message(dc, PIECE + tobinary(1) + tobinary(0) + 'abc')
    co.got_message(dc, PIECE + tobinary(1) + tobinary(3) + 'def')
    co.connection_flushed(dc)
    cc.send_bitfield(chr(0x60))
    cc.send_interested()
    cc.send_not_interested()
    cc.send_choke()
    cc.send_unchoke()
    cc.send_have(4)
    cc.send_request(0, 2, 1)
    cc.send_cancel(1, 2, 3)
    cc.send_piece(1, 2, 'abc')
    co.connection_lost(dc)
    x = ['made upload', 'made download', 'made', 
        ('bitfield', chr(0xC0)), 'choke', 'unchoke',
        'interested', 'not interested', ('have', 2), 
        ('request', 1, 5, 6), ('cancel', 2, 3, 4),
        ('piece', 1, 0, 'abc'), ('piece', 1, 3, 'def'), 
        ('m', HAVE + tobinary(1)),
        'flushed', ('m', BITFIELD + chr(0x60)), ('m', INTERESTED), 
        ('m', NOT_INTERESTED), ('m', CHOKE), ('m', UNCHOKE), 
        ('m', HAVE + tobinary(4)), ('m', REQUEST + tobinary(0) + 
        tobinary(2) + tobinary(1)), ('m', CANCEL + tobinary(1) + 
        tobinary(2) + tobinary(3)), ('m', PIECE + tobinary(1) + 
        tobinary(2) + 'abc'), 'disconnected', 'lost']
    for a, b in zip (events, x):
        assert a == b, repr((a, b))

def test_conversion():
    assert toint(tobinary(50000)) == 50000
