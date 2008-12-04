#! /usr/bin/python

# Written by Bram Cohen
# see LICENSE.txt for license information

from sys import argv
from os.path import getsize, split, join, abspath, isdir
from os import listdir
from sha import sha
from copy import copy
from string import strip
from BitTorrent.bencode import bencode
from BitTorrent.btformats import check_info
from BitTorrent.parseargs import parseargs, formatDefinitions
from threading import Event
from time import time

defaults = [
    ('piece_size_pow2', 18,
        "which power of 2 to set the piece size to"),
    ('comment', '',
        "optional human-readable comment to put in .torrent"),
    ('target', '',
        "optional target file for the torrent")
    ]

ignore = ['core', 'CVS']

def dummy(v):
    pass

def make_meta_file(file, url, piece_len_exp = 18, 
        flag = Event(), progress = dummy, progress_percent=1, comment = None, target = None):
    if piece_len_exp == None:
        piece_len_exp = 18
    piece_length = 2 ** piece_len_exp
    a, b = split(file)
    if not target:
        if b == '':
            f = a + '.torrent'
        else:
            f = join(a, b + '.torrent')
    else:
        f = target
    info = makeinfo(file, piece_length, flag, progress, progress_percent)
    if flag.isSet():
        return
    check_info(info)
    h = open(f, 'wb')
    data = {'info': info, 'announce': strip(url), 'creation date': long(time())}
    if comment:
        data['comment'] = comment
    h.write(bencode(data))
    h.close()

def calcsize(file):
    if not isdir(file):
        return getsize(file)
    total = 0
    for s in subfiles(abspath(file)):
        total += getsize(s[1])
    return total

def makeinfo(file, piece_length, flag, progress, progress_percent=1):
    file = abspath(file)
    if isdir(file):
        subs = subfiles(file)
        subs.sort()
        pieces = []
        sh = sha()
        done = 0
        fs = []
        totalsize = 0.0
        totalhashed = 0
        for p, f in subs:
            totalsize += getsize(f)

        for p, f in subs:
            pos = 0
            size = getsize(f)
            fs.append({'length': size, 'path': p})
            h = open(f, 'rb')
            while pos < size:
                a = min(size - pos, piece_length - done)
                sh.update(h.read(a))
                if flag.isSet():
                    return
                done += a
                pos += a
                totalhashed += a
                
                if done == piece_length:
                    pieces.append(sh.digest())
                    done = 0
                    sh = sha()
                if progress_percent:
                    progress(totalhashed / totalsize)
                else:
                    progress(a)
            h.close()
        if done > 0:
            pieces.append(sh.digest())
        return {'pieces': ''.join(pieces),
            'piece length': piece_length, 'files': fs, 
            'name': split(file)[1]}
    else:
        size = getsize(file)
        pieces = []
        p = 0
        h = open(file, 'rb')
        while p < size:
            x = h.read(min(piece_length, size - p))
            if flag.isSet():
                return
            pieces.append(sha(x).digest())
            p += piece_length
            if p > size:
                p = size
            if progress_percent:
                progress(float(p) / size)
            else:
                progress(min(piece_length, size - p))
        h.close()
        return {'pieces': ''.join(pieces), 
            'piece length': piece_length, 'length': size, 
            'name': split(file)[1]}

def subfiles(d):
    r = []
    stack = [([], d)]
    while len(stack) > 0:
        p, n = stack.pop()
        if isdir(n):
            for s in listdir(n):
                if s not in ignore and s[:1] != '.':
                    stack.append((copy(p) + [s], join(n, s)))
        else:
            r.append((p, n))
    return r

def prog(amount):
    print '%.1f%% complete\r' % (amount * 100),

if __name__ == '__main__':
    if len(argv) < 3:
        print 'usage is -'
        print argv[0] + ' file trackerurl [params]'
        print
        print formatDefinitions(defaults, 80)
    else:
        try:
            config, args = parseargs(argv[3:], defaults, 0, 0)
            make_meta_file(argv[1], argv[2], config['piece_size_pow2'], progress = prog,
                comment = config['comment'], target = config['target'])
        except ValueError, e:
            print 'error: ' + str(e)
            print 'run with no args for parameter explanations'
