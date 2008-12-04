# Written by Bram Cohen
# see LICENSE.txt for license information

from zurllib import urlopen, quote
from btformats import check_peers
from bencode import bdecode
from threading import Thread, Lock
from socket import error
from time import time
from random import randrange
from binascii import b2a_hex

class Rerequester:
    def __init__(self, url, interval, sched, howmany, minpeers, 
            connect, externalsched, amount_left, up, down,
            port, ip, myid, infohash, timeout, errorfunc, maxpeers, doneflag,
            upratefunc, downratefunc, ever_got_incoming):
        self.url = ('%s?info_hash=%s&peer_id=%s&port=%s&key=%s' %
            (url, quote(infohash), quote(myid), str(port),
            b2a_hex(''.join([chr(randrange(256)) for i in xrange(4)]))))
        if ip != '':
            self.url += '&ip=' + quote(ip)
        self.interval = interval
        self.last = None
        self.trackerid = None
        self.announce_interval = 30 * 60
        self.sched = sched
        self.howmany = howmany
        self.minpeers = minpeers
        self.connect = connect
        self.externalsched = externalsched
        self.amount_left = amount_left
        self.up = up
        self.down = down
        self.timeout = timeout
        self.errorfunc = errorfunc
        self.maxpeers = maxpeers
        self.doneflag = doneflag
        self.upratefunc = upratefunc
        self.downratefunc = downratefunc
        self.ever_got_incoming = ever_got_incoming
        self.last_failed = True
        self.last_time = 0

    def c(self):
        self.sched(self.c, self.interval)
        if self.ever_got_incoming():
            getmore = self.howmany() <= self.minpeers / 3
        else:
            getmore = self.howmany() < self.minpeers
        if getmore or time() - self.last_time > self.announce_interval:
            self.announce()

    def begin(self):
        self.sched(self.c, self.interval)
        self.announce(0)

    def announce(self, event = None):
        self.last_time = time()
        s = ('%s&uploaded=%s&downloaded=%s&left=%s' %
            (self.url, str(self.up()), str(self.down()), 
            str(self.amount_left())))
        if self.last is not None:
            s += '&last=' + quote(str(self.last))
        if self.trackerid is not None:
            s += '&trackerid=' + quote(str(self.trackerid))
        if self.howmany() >= self.maxpeers:
            s += '&numwant=0'
        else:
            s += '&compact=1'
        if event != None:
            s += '&event=' + ['started', 'completed', 'stopped'][event]
        set = SetOnce().set
        def checkfail(self = self, set = set):
            if set():
                if self.last_failed and self.upratefunc() < 100 and self.downratefunc() < 100:
                    self.errorfunc('Problem connecting to tracker - timeout exceeded')
                self.last_failed = True
        self.sched(checkfail, self.timeout)
        Thread(target = self.rerequest, args = [s, set]).start()

    def rerequest(self, url, set):
        try:
            h = urlopen(url)
            r = h.read()
            h.close()
            if set():
                def add(self = self, r = r):
                    self.last_failed = False
                    self.postrequest(r)
                self.externalsched(add, 0)
        except (IOError, error), e:
            if set():
                def fail(self = self, r = 'Problem connecting to tracker - ' + str(e)):
                    if self.last_failed:
                        self.errorfunc(r)
                    self.last_failed = True
                self.externalsched(fail, 0)

    def postrequest(self, data):
        try:
            r = bdecode(data)
            check_peers(r)
            if r.has_key('failure reason'):
                self.errorfunc('rejected by tracker - ' + r['failure reason'])
            else:
                if r.has_key('warning message'):
                    self.errorfunc('warning from tracker - ' + r['warning message'])
                self.announce_interval = r.get('interval', self.announce_interval)
                self.interval = r.get('min interval', self.interval)
                self.trackerid = r.get('tracker id', self.trackerid)
                self.last = r.get('last')
                p = r['peers']
                peers = []
                if type(p) == type(''):
                    for x in xrange(0, len(p), 6):
                        ip = '.'.join([str(ord(i)) for i in p[x:x+4]])
                        port = (ord(p[x+4]) << 8) | ord(p[x+5])
                        peers.append((ip, port, None))
                else:
                    for x in p:
                        peers.append((x['ip'], x['port'], x.get('peer id')))
                ps = len(peers) + self.howmany()
                if ps < self.maxpeers:
                    if self.doneflag.isSet():
                        if r.get('num peers', 1000) - r.get('done peers', 0) > ps * 1.2:
                            self.last = None
                    else:
                        if r.get('num peers', 1000) > ps * 1.2:
                            self.last = None
                for x in peers:
                    self.connect((x[0], x[1]), x[2])
        except ValueError, e:
            if data != '':
                self.errorfunc('bad data from tracker - ' + str(e))

class SetOnce:
    def __init__(self):
        self.lock = Lock()
        self.first = True

    def set(self):
        try:
            self.lock.acquire()
            r = self.first
            self.first = False
            return r
        finally:
            self.lock.release()

