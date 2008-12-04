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

'''
Pack.py packs a python script with all its dependencies into an executable file. The
script dependencies are first analyzed and the modules copied into the working
directory, the python.dll is also added to the directory. The directory is then
compressed with lzma and the pylauncher header is added to it, which in turn
extracts the content and launches the script when the executable is run.
'''

import sys
import os
import shutil
from modulegraph.find_modules import find_modules
from modulegraph.modulegraph import SourceModule, Package, Script
from os.path import abspath, join, basename, dirname, exists
import py_compile

def ajoin(*args):
    return abspath(join(*args))

def makedirs(target_path):
    try:
        os.makedirs(target_path)
    except:
        pass

def add_modules(script, target_lib):
    mf = find_modules((script,))
    modules = mf.flatten()
    for module in modules:
        if not module.filename:
            continue
        if isinstance(module, SourceModule):
            target_path = ajoin(target_lib, module.identifier.replace('.','/') + '.pyc')
            makedirs(dirname(target_path))
            print "compiling %s -> %s" % (module.filename, target_path)
            py_compile.compile(module.filename, target_path)
        elif isinstance(module, Package):
            target_path = ajoin(target_lib, module.identifier.replace('.','/'), '__init__.pyc')
            makedirs(dirname(target_path))
            print "compiling %s -> %s" % (module.filename, target_path)
            py_compile.compile(module.filename, target_path)
        elif isinstance(module, Script):
            script_name = os.path.splitext(basename(module.identifier))[0] + '.pyc'
            target_path = ajoin(dirname(target_lib), script_name)
            makedirs(dirname(target_path))
            print "compiling %s -> %s" % (module.filename, target_path)
            py_compile.compile(module.filename, target_path)
        else:
            target_path = ajoin(target_lib, module.identifier.replace('.','/'))
            target_path = dirname(target_path)
            makedirs(target_path)
            print "copying %s -> %s" % (module.filename, target_path)
            shutil.copy(module.filename, target_path)

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
    pylauncher = ajoin(dirname(__file__), 'pylauncher.exe')
    archive = ajoin(dirname(target_dir),'archive.7z')
    target = ajoin(dirname(target_dir), 'application.exe')
    print "Creating self extracting file %s" % target
    cat(target, pylauncher, archive)

def add_python_dll(target_dir):
    #TBD detect the dll/lib of the current python instance
    pythondll = join(dirname(__file__), 'python23.dll')
    shutil.copy(pythondll, target_dir)

def pack(script, target_dir, extras):
    target_dir = join(target_dir, 'files')
    target_lib = join(target_dir, 'lib')

    if exists(target_lib):
        raise Exception("Target directory %s already exists" % target_lib)

    add_modules(script, target_lib)

    #Add other dirs
    for extra in extras:
        target_path = ajoin(target_dir,basename(extra))
        print "copying %s -> %s" % (extra, target_path)
        shutil.copytree(extra, target_path)

    add_python_dll(target_dir)
    compress(target_dir)
    make_self_extracting_exe(target_dir)

if __name__ == "__main__":
    script = sys.argv[1]
    target_dir = sys.argv[2]
    extras = sys.argv[3:]
    pack(script, target_dir, extras)
