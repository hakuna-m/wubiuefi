# Written by Bram Cohen
# see LICENSE.txt for license information

from cStringIO import StringIO
from binascii import b2a_hex
from socket import error as socketerror

protocol_name = 'BitTorrent protocol'

def toint(s):
    return long(b2a_hex(s), 16)

def tobinary(i):
    return (chr(i >> 24) + chr((i >> 16) & 0xFF) + 
        chr((i >> 8) & 0xFF) + chr(i & 0xFF))

# header, reserved, download id, my id, [length, message]

class Connection:
    def __init__(self, Encoder, connection, id, is_local):
        self.encoder = Encoder
        self.connection = connection
        self.id = id
        self.locally_initiated = is_local
        self.complete = False
        self.closed = False
        self.buffer = StringIO()
        self.next_len = 1
        self.next_func = self.read_header_len
        if self.locally_initiated:
            connection.write(chr(len(protocol_name)) + protocol_name + 
                (chr(0) * 8) + self.encoder.download_id)
            if self.id is not None:
                connection.write(self.encoder.my_id)

    def get_ip(self):
        return self.connection.get_ip()

    def get_id(self):
        return self.id

    def is_locally_initiated(self):
        return self.locally_initiated

    def is_flushed(self):
        return self.connection.is_flushed()

    def read_header_len(self, s):
        if ord(s) != len(protocol_name):
            return None
        return len(protocol_name), self.read_header

    def read_header(self, s):
        if s != protocol_name:
            return None
        return 8, self.read_reserved

    def read_reserved(self, s):
        return 20, self.read_download_id

    def read_download_id(self, s):
        if s != self.encoder.download_id:
            return None
        if not self.locally_initiated:
            self.connection.write(chr(len(protocol_name)) + protocol_name + 
                (chr(0) * 8) + self.encoder.download_id + self.encoder.my_id)
        return 20, self.read_peer_id

    def read_peer_id(self, s):
        if not self.id:
            if s == self.encoder.my_id:
                return None
            for v in self.encoder.connections.values():
                if s and v.id == s:
                    return None
            self.id = s
            if self.locally_initiated:
                self.connection.write(self.encoder.my_id)
            else:
                self.encoder.everinc = True
        else:
            if s != self.id:
                return None
        self.complete = True
        self.encoder.connecter.connection_made(self)
        return 4, self.read_len

    def read_len(self, s):
        l = toint(s)
        if l > self.encoder.max_len:
            return None
        return l, self.read_message

    def read_message(self, s):
        if s != '':
            self.encoder.connecter.got_message(self, s)
        return 4, self.read_len

    def read_dead(self, s):
        return None

    def close(self):
        if not self.closed:
            self.connection.close()
            self.sever()

    def sever(self):
        self.closed = True
        del self.encoder.connections[self.connection]
        if self.complete:
            self.encoder.connecter.connection_lost(self)

    def send_message(self, message):
        self.connection.write(tobinary(len(message)) + message)

    def data_came_in(self, s):
        while True:
            if self.closed:
                return
            i = self.next_len - self.buffer.tell()
            if i > len(s):
                self.buffer.write(s)
                return
            self.buffer.write(s[:i])
            s = s[i:]
            m = self.buffer.getvalue()
            self.buffer.reset()
            self.buffer.truncate()
            try:
                x = self.next_func(m)
            except:
                self.next_len, self.next_func = 1, self.read_dead
                raise
            if x is None:
                self.close()
                return
            self.next_len, self.next_func = x

class Encoder:
    def __init__(self, connecter, raw_server, my_id, max_len,
            schedulefunc, keepalive_delay, download_id, 
            max_initiate = 40):
        self.raw_server = raw_server
        self.connecter = connecter
        self.my_id = my_id
        self.max_len = max_len
        self.schedulefunc = schedulefunc
        self.keepalive_delay = keepalive_delay
        self.download_id = download_id
        self.max_initiate = max_initiate
        self.everinc = False
        self.connections = {}
        self.spares = []
        schedulefunc(self.send_keepalives, keepalive_delay)

    def send_keepalives(self):
        self.schedulefunc(self.send_keepalives, self.keepalive_delay)
        for c in self.connections.values():
            if c.complete:
                c.send_message('')

    def start_connection(self, dns, id):
        if id:
            if id == self.my_id:
                return
            for v in self.connections.values():
                if v.id == id:
                    return
        if len(self.connections) >= self.max_initiate:
            if len(self.spares) < self.max_initiate and dns not in self.spares:
                self.spares.append(dns)
            return
        try:
            c = self.raw_server.start_connection(dns)
            self.connections[c] = Connection(self, c, id, True)
        except socketerror:
            pass
    
    def _start_connection(self, dns, id):
        def foo(self=self, dns=dns, id=id):
            self.start_connection(dns, id)
        
        self.schedulefunc(foo, 0)
        
    def got_id(self, connection):
        for v in self.connections.values():
            if connection is not v and connection.id == v.id:
                connection.close()
                return
        self.connecter.connection_made(connection)

    def ever_got_incoming(self):
        return self.everinc

    def external_connection_made(self, connection):
        self.connections[connection] = Connection(self, 
            connection, None, False)

    def connection_flushed(self, connection):
        c = self.connections[connection]
        if c.complete:
            self.connecter.connection_flushed(c)

    def connection_lost(self, connection):
        self.connections[connection].sever()
        while len(self.connections) < self.max_initiate and self.spares:
            self.start_connection(self.spares.pop(), None)

    def data_came_in(self, connection, data):
        self.connections[connection].data_came_in(data)

# everything below is for testing

class DummyConnecter:
    def __init__(self):
        self.log = []
        self.close_next = False
    
    def connection_made(self, connection):
        self.log.append(('made', connection))
        
    def connection_lost(self, connection):
        self.log.append(('lost', connection))

    def connection_flushed(self, connection):
        self.log.append(('flushed', connection))

    def got_message(self, connection, message):
        self.log.append(('got', connection, message))
        if self.close_next:
            connection.close()

class DummyRawServer:
    def __init__(self):
        self.connects = []
    
    def start_connection(self, dns):
        c = DummyRawConnection()
        self.connects.append((dns, c))
        return c

class DummyRawConnection:
    def __init__(self):
        self.closed = False
        self.data = []
        self.flushed = True

    def get_ip(self):
        return 'fake.ip'

    def is_flushed(self):
        return self.flushed

    def write(self, data):
        assert not self.closed
        self.data.append(data)
        
    def close(self):
        assert not self.closed
        self.closed = True

    def pop(self):
        r = ''.join(self.data)
        del self.data[:]
        return r

def dummyschedule(a, b):
    pass

def test_messages_in_and_out():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, 'b' * 20)
    assert c1.pop() == ''
    assert len(c.log) == 1
    assert c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert rs.connects == []
    assert not c1.closed
    assert ch.get_ip() == 'fake.ip'
    
    ch.send_message('abc')
    assert c1.pop() == chr(0) * 3 + chr(3) + 'abc'
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed
    
    e.data_came_in(c1, chr(0) * 3 + chr(3) + 'def')
    assert c1.pop() == ''
    assert c.log == [('got', ch, 'def')]
    del c.log[:]
    assert rs.connects == []
    assert not c1.closed

def test_flushed():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed
    
    e.connection_flushed(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, 'b' * 20)
    assert c1.pop() == ''
    assert len(c.log) == 1
    assert c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert rs.connects == []
    assert not c1.closed
    assert ch.is_flushed()
    
    e.connection_flushed(c1)
    assert c1.pop() == ''
    assert c.log == [('flushed', ch)]
    assert rs.connects == []
    assert not c1.closed
    
    c1.flushed = False
    assert not ch.is_flushed()
    
def test_wrong_header_length():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(5) * 30)
    assert c.log == []
    assert c1.closed

def test_wrong_header():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + 'a' * len(protocol_name))
    assert c.log == []
    assert c1.closed
    
def test_wrong_download_id():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'e' * 20)
    assert c1.pop() == ''
    assert c.log == []
    assert c1.closed

def test_wrong_other_id():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    e.start_connection('dns', 'o' * 20)
    assert c.log == []
    assert len(rs.connects) == 1
    assert rs.connects[0][0] == 'dns'
    c1 = rs.connects[0][1]
    del rs.connects[:]
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'b' * 20)
    assert c.log == []
    assert c1.closed

def test_over_max_len():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert not c1.closed

    e.data_came_in(c1, chr(1) + chr(0) * 3)
    assert c.log == [('lost', ch)]
    assert c1.closed

def test_keepalive():
    s = []
    def sched(interval, thing, s = s):
        s.append((interval, thing))
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, sched, 30, 'd' * 20)
    assert len(s) == 1
    assert s[0][1] == 30
    kfunc = s[0][0]
    del s[:]
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert not c1.closed

    kfunc()
    assert c1.pop() == ''
    assert c.log == []
    assert not c1.closed
    assert s == [(kfunc, 30)]
    del s[:]

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    del c.log[:]
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert not c1.closed

    kfunc()
    assert c1.pop() == chr(0) * 4
    assert c.log == []
    assert not c1.closed

def test_swallow_keepalive():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    del c.log[:]
    assert not c1.closed

    e.data_came_in(c1, chr(0) * 4)
    assert c.log == []
    assert not c1.closed

def test_local_close():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert not c1.closed

    ch.close()
    assert c.log == [('lost', ch)]
    del c.log[:]
    assert c1.closed

def test_local_close_in_message_receive():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert not c1.closed

    c.close_next = True
    e.data_came_in(c1, chr(0) * 3 + chr(4) + 'abcd')
    assert c.log == [('got', ch, 'abcd'), ('lost', ch)]
    assert c1.closed

def test_remote_close():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    ch = c.log[0][1]
    del c.log[:]
    assert not c1.closed

    e.connection_lost(c1)
    assert c.log == [('lost', ch)]
    assert not c1.closed

def test_partial_data_in():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 4)
    e.data_came_in(c1, chr(0) * 4 + 'd' * 20 + 'c' * 10)
    e.data_came_in(c1, 'c' * 10)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    del c.log[:]
    assert not c1.closed
    
def test_ignore_connect_of_extant():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()
    e.external_connection_made(c1)
    assert c1.pop() == ''
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

    e.data_came_in(c1, chr(len(protocol_name)) + protocol_name + 
        chr(0) * 8 + 'd' * 20 + 'o' * 20)
    assert c1.pop() == chr(len(protocol_name)) + protocol_name + \
        chr(0) * 8 + 'd' * 20 + 'a' * 20
    assert len(c.log) == 1 and c.log[0][0] == 'made'
    del c.log[:]
    assert not c1.closed

    e.start_connection('dns', 'o' * 20)
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

def test_ignore_connect_to_self():
    c = DummyConnecter()
    rs = DummyRawServer()
    e = Encoder(c, rs, 'a' * 20, 500, dummyschedule, 30, 'd' * 20)
    c1 = DummyRawConnection()

    e.start_connection('dns', 'a' * 20)
    assert c.log == []
    assert rs.connects == []
    assert not c1.closed

def test_conversion():
    assert toint(tobinary(50000)) == 50000

