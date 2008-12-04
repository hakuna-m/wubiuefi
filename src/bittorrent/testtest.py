"""
A much simpler testing framework than PyUnit

tests a module by running all functions in it whose name starts with 'test'

a test fails if it raises an exception, otherwise it passes

functions are try_all and try_single
"""

# Written by Bram Cohen
# see LICENSE.txt for license information

from traceback import print_exc
from sys import modules

def try_all(excludes = [], excluded_paths=[]):
    """
    tests all imported modules

    takes an optional list of module names and/or module objects to skip over.
    modules from files under under any of excluded_paths are also skipped.
    """
    failed = []
    for modulename, module in modules.items():
        # skip builtins
        if not hasattr(module, '__file__'):
            continue
        # skip modules under any of excluded_paths
        if [p for p in excluded_paths if module.__file__.startswith(p)]:
            continue
        if modulename not in excludes and module not in excludes:
            try_module(module, modulename, failed)
    print_failed(failed)

def try_single(m):
    """
    tests a single module
    
    accepts either a module object or a module name in string form
    """
    if type(m) is str:
        modulename = m
        module = __import__(m)
    else:
        modulename = str(m)
        module = m
    failed = []
    try_module(module, modulename, failed)
    print_failed(failed)

def try_module(module, modulename, failed):
    if not hasattr(module, '__dict__'):
        return
    for n, func in module.__dict__.items():
        if not callable(func) or n[:4] != 'test':
            continue
        name = modulename + '.' + n
        try:
            print 'trying ' + name
            func()
            print 'passed ' + name
        except:
            print_exc()
            failed.append(name)
            print 'failed ' + name

def print_failed(failed):
    print
    if len(failed) == 0:
        print 'everything passed'
    else:
        print 'the following tests failed:'
        for i in failed:
            print i



