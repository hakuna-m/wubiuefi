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
from modulegraph.find_modules import find_modules
from modulegraph.modulegraph import SourceModule, Package, Script, Extension
from os.path import basename, dirname
import py_compile
from optparse import OptionParser
import logging
from version import *

log = logging.getLogger(__name__)

class Application(object):
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)

    def run(self):
        self.localize()
        self.parse_commandline_arguments()
        self.set_logger()
        self.create_dirs()
        self.add_dependencies(self.main_script)
        self.add_extras()

    def localize(self):
        try:
            import gettext
            gettext.install(APPLICATION_NAME)
        except ImportError:
            import __builtin__
            def dummytrans (text):
                """A _ function for systems without gettext. Effectively a NOOP"""
                return text
            __builtin__.__dict__['_'] = dummytrans

    def print_readme(self):
        readme = ajoin(self.root_dir, 'README')
        readme = open(readme, 'r')
        content = readme.read()
        readme.close()
        print content

    def parse_commandline_arguments(self):
        usage = "%prog [options] main_script [extra extra extra]"
        version = version="%s-rev%s" % (APPLICATION_VERSION, APPLICATION_REVISION)
        description='Pypack packages a script into a directory containing all needed depencies suitable for "folder deployment". Run `python pypack --readme` for more information.'
        parser = OptionParser(usage=usage, description = description, version = version)
        parser.add_option("--readme", action="store_true", dest="readme", help="show more information")
        parser.add_option("--verbose", action="store_true", dest="verbose", help="run in verbose mode, all messages are displayed")
        parser.add_option("--debug", action="store_true", dest="debug", help="print debug messages to stdout")
        parser.add_option("--print", action="store_true", dest="print_dependencies", help="print dependencies and exit")
        parser.add_option("--outputdir", dest="out_dir", default="./build", help="directory where the files will be built, if non existent, it will be created")
        parser.add_option("--bytecompile", action="store_true", dest="bytecompile", help="bytecompile the python files")
        options, args = parser.parse_args()
        self.options, args = parser.parse_args()
        if options.readme:
            print self.print_readme()
            sys.exit(0)
        if not len(args):
            parser.print_help()
            sys.exit(1)
        self.main_script = args[0]
        self.extras = args[1:]
        if self.options.debug:
            self.options.verbose = True
        if self.options.print_dependencies:
            self.print_dependencies()
            sys.exit(0)

    def create_dirs(self):
        self.out_dir = self.options.out_dir
        self.out_dir = ajoin(self.out_dir)
        if os.path.exists(self.out_dir):
            print 'ERROR: the build directory "%s" already exists.\nRemove that before running %s again.' % (self.out_dir, APPLICATION_NAME)
            sys.exit(1)
        self.lib_dir = ajoin(self.out_dir, 'lib')
        os.makedirs(self.lib_dir)

    def set_logger(self):
        '''
        Adjust the application root logger settings
        '''
        root_logger = logging.getLogger()
        if root_logger.handlers:
            handler = root_logger.handlers[0]
        else:
            handler = logging.StreamHandler()
            root_logger.addHandler(handler)
        formatter = logging.Formatter('%(message)s', datefmt='%m-%d %H:%M')
        handler.setFormatter(formatter)
        root_logger.setLevel(logging.DEBUG)
        if self.options.verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.ERROR)

    def print_dependencies(self):
        scripts = [self.main_script]
        scripts += [f for f in self.extras if f[:-3] == '.py']
        modules = []
        for script in scripts:
            for m in get_modules(script):
                modules.append(m)
        for m in modules:
            print m

    def add_dependencies(self, script):
        '''
        Adds all dependencies to lib_dir
        '''
        modules = get_modules(script)
        lib_dir = self.lib_dir
        for module in modules:
            if not module.filename:
                continue
            if isinstance(module, SourceModule):
                target = module2path(lib_dir, module.identifier)
                target +=  '.py'
                self.compile(module.filename, target)
            elif isinstance(module, Package):
                target = module2path(lib_dir, module.identifier)
                target = ajoin(target, '__init__.py')
                self.compile(module.filename, target)
            elif isinstance(module, Script):
                log.debug("Script %s", script)
                if module.identifier[0] != "_":
                    script_name = basename(script)
                    target = ajoin(self.out_dir, script_name)
                    self.compile(module.filename, target)
            elif isinstance(module, Extension):
                target = module2path(lib_dir, module.identifier)
                target = dirname(target)
                makedirs(target)
                log.debug("copying %s -> %s" % (module.filename, target))
                shutil.copy(module.filename, target)
            else:
                log.error("Unkown module %s", module)

    def compile(self, source, target):
        log.debug("copying %s -> %s", source, target)
        makedirs(dirname(target))
        shutil.copy(source, target)
        if self.options.bytecompile:
            log.debug("compiling %s", target)
            dfile = target
            if target.startswith(self.out_dir):
                dfile = target[len(self.out_dir):]
            py_compile.compile(target, dfile=dfile, doraise=True)
            os.unlink(target)

    def add_extras(self):
        '''
        Add extra files, modules, pacakges or directories
        '''
        for extra in self.extras:
            if os.path.isfile(extra):
                if extra.endswith('.py'):
                    self.add_dependencies(extra)
                    target = os.path.basename(extra)
                    target = ajoin(self.lib_dir, target)
                    self.compile(extra, target)
                else:
                    target = os.path.basename(extra)
                    target = ajoin(self.out_dir, target)
                    log.debug("copying %s -> %s", extra, target)
                    shutil.copy(extra, target)
            elif os.path.isdir(extra):
                target = os.path.basename(extra)
                target = ajoin(self.out_dir, target)
                log.debug("copying %s -> %s", extra, target)
                shutil.copytree(extra, target, symlinks=False)
            else:
                print 'ERROR: The extra argument "%s" cannot be found' % extra
                sys.exit(1)


def ajoin(*args):
    return os.path.abspath(os.path.join(*args))

def makedirs(target_path):
    try:
        os.makedirs(target_path)
    except:
        pass

def module2path(root_dir, module_name):
    path = module_name.split('.')
    path = ajoin(root_dir, *path)
    return path

def get_modules(script_path):
    sys.path.insert(0, os.path.dirname(script_path))
    mf = find_modules((script_path,))
    del sys.path[0]
    modules = mf.flatten()
    return modules
