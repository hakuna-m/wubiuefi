# Written by Bram Cohen
# see LICENSE.txt for license information

from parseargs import parseargs, formatDefinitions
from RawServer import RawServer
from HTTPHandler import HTTPHandler
from NatCheck import NatCheck
from threading import Event
from bencode import bencode, bdecode, Bencached
from zurllib import urlopen, quote, unquote
from urlparse import urlparse
from os import rename
from os.path import exists, isfile
from cStringIO import StringIO
from time import time, gmtime, strftime
from random import shuffle
from sha import sha
from types import StringType, IntType, LongType, ListType, DictType
from binascii import b2a_hex, a2b_hex, a2b_base64
import sys
from __init__ import version

defaults = [
    ('port', 80, "Port to listen on."),
    ('dfile', None, 'file to store recent downloader info in'),
    ('bind', '', 'ip to bind to locally'),
    ('socket_timeout', 15, 'timeout for closing connections'),
    ('save_dfile_interval', 5 * 60, 'seconds between saving dfile'),
    ('timeout_downloaders_interval', 45 * 60, 'seconds between expiring downloaders'),
    ('reannounce_interval', 30 * 60, 'seconds downloaders should wait between reannouncements'),
    ('response_size', 50, 'number of peers to send in an info message'),
    ('timeout_check_interval', 5,
        'time to wait between checking if any connections have timed out'),
    ('nat_check', 3,
        "how many times to check if a downloader is behind a NAT (0 = don't check)"),
    ('min_time_between_log_flushes', 3.0,
        'minimum time it must have been since the last flush to do another one'),
    ('allowed_dir', '', 'only allow downloads for .torrents in this dir'),
    ('parse_allowed_interval', 15, 'minutes between reloading of allowed_dir'),
    ('show_names', 1, 'whether to display names from allowed dir'),
    ('favicon', '', 'file containing x-icon data to return when browser requests favicon.ico'),
    ('only_local_override_ip', 1, "ignore the ip GET parameter from machines which aren't on local network IPs"),
    ('logfile', '', 'file to write the tracker logs, use - for stdout (default)'),
    ('allow_get', 0, 'use with allowed_dir; adds a /file?hash={hash} url that allows users to download the torrent file'),
    ('keep_dead', 0, 'keep dead torrents after they expire (so they still show up on your /scrape and web page)'),
    ('max_give', 200, 'maximum number of peers to give with any one request'),
    ]

def statefiletemplate(x):
    if type(x) != DictType:
        raise ValueError
    for cname, cinfo in x.items():
        if cname == 'peers':
            for y in cinfo.values():      # The 'peers' key is a dictionary of SHA hashes (torrent ids)
                 if type(y) != DictType:   # ... for the active torrents, and each is a dictionary
                     raise ValueError
                 for id, info in y.items(): # ... of client ids interested in that torrent
                     if (len(id) != 20):
                         raise ValueError
                     if type(info) != DictType:  # ... each of which is also a dictionary
                         raise ValueError # ... which has an IP, a Port, and a Bytes Left count for that client for that torrent
                     if type(info.get('ip', '')) != StringType:
                         raise ValueError
                     port = info.get('port')
                     if type(port) not in (IntType, LongType) or port < 0:
                         raise ValueError
                     left = info.get('left')
                     if type(left) not in (IntType, LongType) or left < 0:
                         raise ValueError
        elif cname == 'completed':
            if (type(cinfo) != DictType): # The 'completed' key is a dictionary of SHA hashes (torrent ids)
                raise ValueError          # ... for keeping track of the total completions per torrent
            for y in cinfo.values():      # ... each torrent has an integer value
                if type(y) not in (IntType, LongType):   # ... for the number of reported completions for that torrent
                    raise ValueError

def parseTorrents(dir):
    import os
    a = {}
    for f in os.listdir(dir):
        if f[-8:] == '.torrent':
            try:
                p = os.path.join(dir,f)
                d = bdecode(open(p, 'rb').read())
                h = sha(bencode(d['info'])).digest()
                i = d['info']
                a[h] = {}
                a[h]['name'] = i.get('name', f)
                a[h]['file'] = f
                a[h]['path'] = p
                l = 0
                if i.has_key('length'):
                    l = i.get('length',0)
                elif i.has_key('files'):
                    for li in i['files']:
                        if li.has_key('length'):
                            l = l + li['length']
                a[h]['length'] = l
            except:
                # what now, boss?
                print "Error parsing " + f, sys.exc_info()[0]
    return a

alas = 'your file may exist elsewhere in the universe\nbut alas, not here\n'

def isotime(secs = None):
    if secs == None:
        secs = time()
    return strftime('%Y-%m-%d %H:%M UTC', gmtime(secs))

def compact_peer_info(ip, port):
    return ''.join([chr(int(i)) for i in ip.split('.')]) + chr((port & 0xFF00) >> 8) + chr(port & 0xFF)

class Tracker:
    def __init__(self, config, rawserver):
        self.response_size = config['response_size']
        self.dfile = config['dfile']
        self.natcheck = config['nat_check']
        self.max_give = config['max_give']
        self.reannounce_interval = config['reannounce_interval']
        self.save_dfile_interval = config['save_dfile_interval']
        self.show_names = config['show_names']
        self.only_local_override_ip = config['only_local_override_ip']
        favicon = config['favicon']
        self.favicon = None
        if favicon:
            if isfile(favicon):
                h = open(favicon, 'rb')
                self.favicon = h.read()
                h.close()
            else:
                print "**warning** specified favicon file -- %s -- does not exist." % favicon
        self.rawserver = rawserver
        self.becache1 = {}
        self.becache2 = {}
        self.cache1 = {}
        self.cache2 = {}
        self.times = {}
        if exists(self.dfile):
            h = open(self.dfile, 'rb')
            ds = h.read()
            h.close()
            tempstate = bdecode(ds)
        else:
            tempstate = {}
        if tempstate.has_key('peers'):
            self.state = tempstate
        else:
            self.state = {}
            self.state['peers'] = tempstate
        self.downloads = self.state.setdefault('peers', {})
        self.completed = self.state.setdefault('completed', {})
        statefiletemplate(self.state)
        for x, dl in self.downloads.items():
            self.times[x] = {}
            for y, dat in dl.items():
                self.times[x][y] = 0
                if not dat.get('nat',1):
                    ip = dat['ip']
                    gip = dat.get('given ip')
                    if gip and is_valid_ipv4(gip) and (not self.only_local_override_ip or is_local_ip(ip)):
                        ip = gip
                    self.becache1.setdefault(x,{})[y] = Bencached(bencode({'ip': ip, 
                        'port': dat['port'], 'peer id': y}))
                    self.becache2.setdefault(x,{})[y] = compact_peer_info(ip, dat['port'])
        rawserver.add_task(self.save_dfile, self.save_dfile_interval)
        self.prevtime = time()
        self.timeout_downloaders_interval = config['timeout_downloaders_interval']
        rawserver.add_task(self.expire_downloaders, self.timeout_downloaders_interval)
        self.logfile = None
        self.log = None
        if (config['logfile'] != '') and (config['logfile'] != '-'):
            try:
                self.logfile = config['logfile']
                self.log = open(self.logfile,'a')
                sys.stdout = self.log
                print "# Log Started: ", isotime()
            except:
                print "Error trying to redirect stdout to log file:", sys.exc_info()[0]
        self.allow_get = config['allow_get']
        if config['allowed_dir'] != '':
            self.allowed_dir = config['allowed_dir']
            self.parse_allowed_interval = config['parse_allowed_interval']
            self.parse_allowed()
        else:
            self.allowed = None
        if unquote('+') != ' ':
            self.uq_broken = 1
        else:
            self.uq_broken = 0
        self.keep_dead = config['keep_dead']

    def get(self, connection, path, headers):
        try:
            (scheme, netloc, path, pars, query, fragment) = urlparse(path)
            if self.uq_broken == 1:
                path = path.replace('+',' ')
                query = query.replace('+',' ')
            path = unquote(path)[1:]
            params = {}
            for s in query.split('&'):
                if s != '':
                    i = s.index('=')
                    params[unquote(s[:i])] = unquote(s[i+1:])
        except ValueError, e:
            return (400, 'Bad Request', {'Content-Type': 'text/plain'}, 
                    'you sent me garbage - ' + str(e))
        if path == '' or path == 'index.html':
            s = StringIO()
            s.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n' \
                '<html><head><title>BitTorrent download info</title>\n')
            if self.favicon != None:
                s.write('<link rel="shortcut icon" href="/favicon.ico" />\n')
            s.write('</head>\n<body>\n' \
                '<h3>BitTorrent download info</h3>\n'\
                '<ul>\n'
                '<li><strong>tracker version:</strong> %s</li>\n' \
                '<li><strong>server time:</strong> %s</li>\n' \
                '</ul>\n' % (version, isotime()))
            names = self.downloads.keys()
            if names:
                names.sort()
                tn = 0
                tc = 0
                td = 0
                tt = 0  # Total transferred
                ts = 0  # Total size
                nf = 0  # Number of files displayed
                uc = {}
                ud = {}
                if self.allowed != None and self.show_names:
                    s.write('<table summary="files" border="1">\n' \
                        '<tr><th>info hash</th><th>torrent name</th><th align="right">size</th><th align="right">complete</th><th align="right">downloading</th><th align="right">downloaded</th><th align="right">transferred</th></tr>\n')
                else:
                    s.write('<table summary="files">\n' \
                        '<tr><th>info hash</th><th align="right">complete</th><th align="right">downloading</th><th align="right">downloaded</th></tr>\n')
                for name in names:
                    l = self.downloads[name]
                    n = self.completed.get(name, 0)
                    tn = tn + n
                    lc = []
                    for i in l.values():
                        if type(i) == DictType:
                            if i['left'] == 0:
                                lc.append(1)
                                uc[i['ip']] = 1
                            else:
                                ud[i['ip']] = 1
                    c = len(lc)
                    tc = tc + c
                    d = len(l) - c
                    td = td + d
                    if self.allowed != None and self.show_names:
                        if self.allowed.has_key(name):
                            nf = nf + 1
                            sz = self.allowed[name]['length']  # size
                            ts = ts + sz
                            szt = sz * n   # Transferred for this torrent
                            tt = tt + szt
                            if self.allow_get == 1:
                                linkname = '<a href="/file?info_hash=' + b2a_hex(name) + '">' + self.allowed[name]['name'] + '</a>'
                            else:
                                linkname = self.allowed[name]['name']
                            s.write('<tr><td><code>%s</code></td><td>%s</td><td align="right">%s</td><td align="right">%i</td><td align="right">%i</td><td align="right">%i</td><td align="right">%s</td></tr>\n' \
                                % (b2a_hex(name), linkname, size_format(sz), c, d, n, size_format(szt)))
                    else:
                        s.write('<tr><td><code>%s</code></td><td align="right"><code>%i</code></td><td align="right"><code>%i</code></td><td align="right"><code>%i</code></td></tr>\n' \
                            % (b2a_hex(name), c, d, n))
                ttn = 0
                for i in self.completed.values():
                    ttn = ttn + i
                if self.allowed != None and self.show_names:
                    s.write('<tr><td align="right" colspan="2">%i files</td><td align="right">%s</td><td align="right">%i/%i</td><td align="right">%i/%i</td><td align="right">%i/%i</td><td align="right">%s</td></tr>\n'
                            % (nf, size_format(ts), len(uc), tc, len(ud), td, tn, ttn, size_format(tt)))
                else:
                    s.write('<tr><td align="right">%i files</td><td align="right">%i/%i</td><td align="right">%i/%i</td><td align="right">%i/%i</td></tr>\n'
                            % (nf, len(uc), tc, len(ud), td, tn, ttn))
                s.write('</table>\n' \
                    '<ul>\n' \
                    '<li><em>info hash:</em> SHA1 hash of the "info" section of the metainfo (*.torrent)</li>\n' \
                    '<li><em>complete:</em> number of connected clients with the complete file (total: unique IPs/total connections)</li>\n' \
                    '<li><em>downloading:</em> number of connected clients still downloading (total: unique IPs/total connections)</li>\n' \
                    '<li><em>downloaded:</em> reported complete downloads (total: current/all)</li>\n' \
                    '<li><em>transferred:</em> torrent size * total downloaded (does not include partial transfers)</li>\n' \
                    '</ul>\n')
            else:
                s.write('<p>not tracking any files yet...</p>\n')
            s.write('</body>\n' \
                '</html>\n')
            return (200, 'OK', {'Content-Type': 'text/html; charset=iso-8859-1'}, s.getvalue())
        elif path == 'scrape':
            fs = {}
            names = []
            if params.has_key('info_hash'):
                if self.downloads.has_key(params['info_hash']):
                    names = [ params['info_hash'] ]
                # else return nothing
            else:
                names = self.downloads.keys()
                names.sort()
            for name in names:
                l = self.downloads[name]
                n = self.completed.get(name, 0)
                c = len([1 for i in l.values() if type(i) == DictType and i['left'] == 0])
                d = len(l) - c
                fs[name] = {'complete': c, 'incomplete': d, 'downloaded': n}
                if (self.allowed is not None) and self.allowed.has_key(name) and self.show_names:
                    fs[name]['name'] = self.allowed[name]['name']
            r = {'files': fs}
            return (200, 'OK', {'Content-Type': 'text/plain'}, bencode(r))
        elif (path == 'file') and (self.allow_get == 1) and params.has_key('info_hash') and self.allowed.has_key(a2b_hex(params['info_hash'])):
            hash = a2b_hex(params['info_hash'])
            fname = self.allowed[hash]['file']
            fpath = self.allowed[hash]['path']
            return (200, 'OK', {'Content-Type': 'application/x-bittorrent', 'Content-Disposition': 'attachment; filename=' + fname}, open(fpath, 'rb').read())
        elif path == 'favicon.ico' and self.favicon != None:
            return (200, 'OK', {'Content-Type' : 'image/x-icon'}, self.favicon)
        if path != 'announce':
            return (404, 'Not Found', {'Content-Type': 'text/plain', 'Pragma': 'no-cache'}, alas)
        try:
            if not params.has_key('info_hash'):
                raise ValueError, 'no info hash'
            if params.has_key('ip') and not is_valid_ipv4(params['ip']):
                raise ValueError('DNS name or invalid IP address given for IP')
            infohash = params['info_hash']
            if self.allowed != None:
                if not self.allowed.has_key(infohash):
                    return (200, 'OK', {'Content-Type': 'text/plain', 'Pragma': 'no-cache'}, bencode({'failure reason':
                    'Requested download is not authorized for use with this tracker.'}))
            ip = connection.get_ip()
            ip_override = 0
            if params.has_key('ip') and is_valid_ipv4(params['ip']) and (
                    not self.only_local_override_ip or is_local_ip(ip)):
                ip_override = 1
            if params.has_key('event') and params['event'] not in ['started', 'completed', 'stopped']:
                raise ValueError, 'invalid event'
            port = long(params.get('port', ''))
            uploaded = long(params.get('uploaded', ''))
            downloaded = long(params.get('downloaded', ''))
            left = long(params.get('left', ''))
            myid = params.get('peer_id', '')
            if len(myid) != 20:
                raise ValueError, 'id not of length 20'
            rsize = self.response_size
            if params.has_key('numwant'):
                rsize = min(long(params['numwant']), self.max_give)
        except ValueError, e:
            return (400, 'Bad Request', {'Content-Type': 'text/plain'}, 
                'you sent me garbage - ' + str(e))
        peers = self.downloads.setdefault(infohash, {})
        self.completed.setdefault(infohash, 0)
        ts = self.times.setdefault(infohash, {})
        confirm = 0
        if peers.has_key(myid):
            myinfo = peers[myid]
            if myinfo.has_key('key'):
                if params.get('key') != myinfo['key']:
                    return (200, 'OK', {'Content-Type': 'text/plain', 'Pragma': 'no-cache'}, 
                        bencode({'failure reason': 'key did not match key supplied earlier'}))
                confirm = 1
            elif myinfo['ip'] == ip:
                confirm = 1
        else:
            confirm = 1
        if params.get('event', '') != 'stopped' and confirm:
            ts[myid] = time()
            if not peers.has_key(myid):
                peers[myid] = {'ip': ip, 'port': port, 'left': left}
                if params.has_key('key'):
                    peers[myid]['key'] = params['key']
                if params.has_key('ip') and is_valid_ipv4(params['ip']):
                    peers[myid]['given ip'] = params['ip']
                mip = ip
                if ip_override:
                    mip = params['ip']
                if not self.natcheck or ip_override:
                    self.becache1.setdefault(infohash,{})[myid] = Bencached(bencode({'ip': mip, 'port': port, 'peer id': myid}))
                    self.becache2.setdefault(infohash,{})[myid] = compact_peer_info(mip, port)
            else:
                peers[myid]['left'] = left
                peers[myid]['ip'] = ip
            if params.get('event', '') == 'completed':
                self.completed[infohash] = 1 + self.completed[infohash]
            if port == 0:
                peers[myid]['nat'] = 2**30
            elif self.natcheck and not ip_override:
                to_nat = peers[myid].get('nat', -1)
                if to_nat and to_nat < self.natcheck:
                    NatCheck(self.connectback_result, infohash, myid, ip, port, self.rawserver)
            else:
                peers[myid]['nat'] = 0
        elif confirm:
            if peers.has_key(myid):
                if self.becache1[infohash].has_key(myid):
                    del self.becache1[infohash][myid]
                    del self.becache2[infohash][myid]
                del peers[myid]
                del ts[myid]
        data = {'interval': self.reannounce_interval}
        if params.get('compact', 0):
            if rsize == 0:
                data['peers'] = ''
            else:
                cache = self.cache2.setdefault(infohash, [])
                if len(cache) < rsize:
                    del cache[:]
                    cache.extend(self.becache2.setdefault(infohash, {}).values())
                    shuffle(cache)
                    del self.cache1.get(infohash, [])[:]
                data['peers'] = ''.join(cache[-rsize:])
                del cache[-rsize:]
        else:
            if rsize == 0:
                data['peers'] = []
            else:
                cache = self.cache1.setdefault(infohash, [])
                if len(cache) < rsize:
                    del cache[:]
                    cache.extend(self.becache1.setdefault(infohash, {}).values())
                    shuffle(cache)
                    del self.cache2.get(infohash, [])[:]
                data['peers'] = cache[-rsize:]
                del cache[-rsize:]
        connection.answer((200, 'OK', {'Content-Type': 'text/plain', 'Pragma': 'no-cache'}, bencode(data)))

    def connectback_result(self, result, downloadid, peerid, ip, port):
        record = self.downloads.get(downloadid, {}).get(peerid)
        if record is None or record['ip'] != ip or record['port'] != port:
            return
        if not record.has_key('nat'):
            record['nat'] = int(not result)
        else:
            if result:
                record['nat'] = 0
            else:
                record['nat'] += 1
        if result:
            self.becache1.setdefault(downloadid,{})[peerid] = Bencached(bencode({'ip': ip, 'port': port, 'peer id': peerid}))
            self.becache2.setdefault(downloadid,{})[peerid] = compact_peer_info(ip, port)

    def save_dfile(self):
        self.rawserver.add_task(self.save_dfile, self.save_dfile_interval)
        h = open(self.dfile, 'wb')
        h.write(bencode(self.state))
        h.close()

    def parse_allowed(self):
        self.rawserver.add_task(self.parse_allowed, self.parse_allowed_interval * 60)
        self.allowed = parseTorrents(self.allowed_dir)
        
    def expire_downloaders(self):
        for x in self.times.keys():
            for myid, t in self.times[x].items():
                if t < self.prevtime:
                    if self.becache1.get(x, {}).has_key(myid):
                        del self.becache1[x][myid]
                        del self.becache2[x][myid]
                    del self.times[x][myid]
                    del self.downloads[x][myid]
        self.prevtime = time()
        if (self.keep_dead != 1):
            for key, value in self.downloads.items():
                if len(value) == 0:
                    del self.times[key]
                    del self.downloads[key]
        self.rawserver.add_task(self.expire_downloaders, self.timeout_downloaders_interval)

def is_valid_ipv4(ip):
    try:
        x = compact_peer_info(ip, 0)
        if len(x) != 6:
            return False
    except (ValueError, IndexError):
        return False
    return True

def is_local_ip(ip):
    try:
        v = [long(x) for x in ip.split('.')]
        if v[0] == 10 or v[0] == 127 or v[:2] in ([192, 168], [169, 254]):
            return 1
        if v[0] == 172 and v[1] >= 16 and v[1] <= 31:
            return 1
    except ValueError:
        return 0

def track(args):
    if len(args) == 0:
        print formatDefinitions(defaults, 80)
        return
    try:
        config, files = parseargs(args, defaults, 0, 0)
    except ValueError, e:
        print 'error: ' + str(e)
        print 'run with no arguments for parameter explanations'
        return
    r = RawServer(Event(), config['timeout_check_interval'], config['socket_timeout'])
    t = Tracker(config, r)
    r.bind(config['port'], config['bind'], True)
    r.listen_forever(HTTPHandler(t.get, config['min_time_between_log_flushes']))
    t.save_dfile()
    print '# Shutting down: ' + isotime()

def size_format(s):
    if (s < 1024):
        r = str(s) + 'B'
    elif (s < 1048576):
        r = str(int(s/1024)) + 'KiB'
    elif (s < 1073741824l):
        r = str(int(s/1048576)) + 'MiB'
    elif (s < 1099511627776l):
        r = str(int((s/1073741824.0)*100.0)/100.0) + 'GiB'
    else:
        r = str(int((s/1099511627776.0)*100.0)/100.0) + 'TiB'
    return(r)

