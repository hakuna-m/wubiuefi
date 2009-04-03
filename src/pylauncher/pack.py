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

Usage:

python pack.py [options] main_script [extra [extra [extra..]]]

Where extras are additional directories or python scripts to be added.
If an extra is a python script, it will be byte compiled and added within lib.
Other extras will simply be copied to the same directory containing
main_script.
'''

import sys
import os
import shutil
from modulegraph.find_modules import find_modules
from modulegraph.modulegraph import SourceModule, Package, Script
from os.path import abspath, join, basename, dirname, exists
import py_compile
from optparse import OptionParser
SIGNATURE="@@@pylauncher@@@"
def ajoin(*args):
    return abspath(join(*args))

def makedirs(target_path):
    try:
        os.makedirs(target_path)
    except:
        pass

def compile(source, target, nopyc):
    print "compiling %s -> %s" % (source, target)
    shutil.copy(source, target)
    if not nopyc:
        py_compile.compile(target, doraise=True)
        os.unlink(target)

def add_modules(script, target_lib, nopyc):
    mf = find_modules((script,))
    modules = mf.flatten()
    for module in modules:
        if not module.filename:
            continue
        if isinstance(module, SourceModule):
            target_path = ajoin(target_lib, module.identifier.replace('.','/') + '.py')
            makedirs(dirname(target_path))
            compile(module.filename, target_path, nopyc)
        elif isinstance(module, Package):
            target_path = ajoin(target_lib, module.identifier.replace('.','/'), '__init__.py')
            makedirs(dirname(target_path))
            compile(module.filename, target_path, nopyc)
        elif isinstance(module, Script):
            script_name = os.path.splitext(basename(module.identifier))[0] + '.py'
            target_path = ajoin(dirname(target_lib), script_name)
            makedirs(dirname(target_path))
            compile(module.filename, target_path, nopyc)
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
    for f in ('pylauncher.exe', 'python23.dll', 'pythonw.exe'):
        source = ajoin(dirname(__file__), f)
        shutil.copy(source, target_dir)

def pack(script, target_dir, extras, nopyc):
    target_dir = ajoin(target_dir, 'files')
    target_lib = ajoin(target_dir, 'lib')

    if exists(target_lib):
        raise Exception("Target directory %s already exists" % target_lib)

    add_modules(script, target_lib, nopyc)

    #Add other dirs
    for extra in extras:
        if os.path.isfile(extra) and extra.endswith('.py'):
            target_path = ajoin(target_lib, os.path.basename(extra))
            compile(extra, target_path, nopyc)
        else:
            target_path = ajoin(target_dir,basename(extra))
            print "copying %s -> %s" % (extra, target_path)
            shutil.copytree(extra, target_path)

    add_python_interpreter(target_dir)
    compress(target_dir)
    make_self_extracting_exe(target_dir)

def parse_arguments():
    usage = "python pack.py [options] main_script [extra [extra [extra..]]]"
    parser = OptionParser(usage=usage)
    parser.add_option("--dir", dest="target_dir", default=".", help="Directory where the files will be built, if non existent, it will be created")
    parser.add_option("--nopyc", action="store_const", const=True, dest="nopyc", help="Do not bytecompile the python files")
    options, args = parser.parse_args()
    script = args[0]
    extras = args[1:]
    nopyc=options.nopyc
    target_dir = options.target_dir
    return  script, target_dir, extras, nopyc

def main():
    script, target_dir, extras, nopyc = parse_arguments()
    pack(script, target_dir, extras, nopyc)

if __name__ == "__main__":
    main()
