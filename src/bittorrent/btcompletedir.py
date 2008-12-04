#! /usr/bin/python

# Written by Bram Cohen
# see LICENSE.txt for license information

from os.path import join, split
from threading import Event
from traceback import print_exc
from sys import argv
from BitTorrent.btmakemetafile import calcsize, make_meta_file, ignore

def dummy(x):
    pass

def completedir(files, url, flag = Event(), vc = dummy, fc = dummy, piece_len_pow2 = None):
    files.sort()
    ext = '.torrent'

    togen = []
    for f in files:
        if f[-len(ext):] != ext:
            togen.append(f)
        
    total = 0
    for i in togen:
        total += calcsize(i)

    subtotal = [0]
    def callback(x, subtotal = subtotal, total = total, vc = vc):
        subtotal[0] += x
        vc(float(subtotal[0]) / total)
    for i in togen:
        t = split(i)
        if t[1] == '':
            i = t[0]
        fc(i)
        try:
            make_meta_file(i, url, flag = flag, progress = callback, progress_percent=0, piece_len_exp = piece_len_pow2)
        except ValueError:
            print_exc()

def dc(v):
    print v

if __name__ == '__main__':
    completedir(argv[2:], argv[1], fc = dc)
