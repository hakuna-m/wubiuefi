#!/usr/bin/env python
#
# Copyright (c) 2007, 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# pack.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# pack.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import sys
import os
import shutil
from os.path import abspath, join, basename, dirname, exists

SIGNATURE="@@@pylauncher@@@"

def ajoin(*args):
    return abspath(join(*args))

def compress(target_dir):
    #TBD the 7z compressor should be properly compiled
    cwd = os.getcwd()
    compressor = ajoin("C:", "Program Files", "7-Zip","7z.exe")
    cmd = '%s a -t7z -m0=lzma -mx=9 -mfb=256 -md=32m -ms=on ../archive.7z *'
    cmd = cmd % (compressor,)
    print cmd
    os.chdir(target_dir)
    os.system(cmd)
    os.chdir(cwd)

def cat(outfile, *infiles):
    fout = open(outfile, 'wb')
    for fname in infiles:
        fin = open(abspath(fname), 'rb')
        data = fin.read()
        fin.close()
        fout.write(data)
    fout.close()

def make_self_extracting_exe(target_dir):
    header = ajoin(dirname(__file__), 'header.exe')
    archive = ajoin(dirname(target_dir),'archive.7z')
    target = ajoin(dirname(target_dir), 'application.exe')
    signature = ajoin(dirname(target_dir), 'signature')
    f = open(signature, 'wb')
    f.write(SIGNATURE)
    f.close()
    print "Creating self extracting file %s" % target
    cat(target, header, signature, archive)

def add_python_interpreter(target_dir):
    #TBD detect the dll/lib of the current python instance
    for f in ('pylauncher.exe', 'python23.dll', 'pyrun.exe'):
        source = ajoin(dirname(__file__), f)
        shutil.copy(source, target_dir)

def main():
    target_dir = sys.argv[1]
    add_python_interpreter(target_dir)
    compress(target_dir)
    make_self_extracting_exe(target_dir)

if __name__ == "__main__":
    main()
