#!/usr/bin/env python

import module_finder as mf
import bin_finder as bf
import sys
import os

thisdir = os.path.abspath(os.path.dirname(__file__))
srcdir = os.path.abspath(sys.argv[2]) #os.path.dirname(thisdir)
script = os.path.abspath(sys.argv[1]) #os.path.join(srcdir, "wubi", "wubi.py")
scriptdir = os.path.dirname(script)

it = mf.ImportTracker()
it.path.append(srcdir)
it.path.append(scriptdir)
it.analyze_r(script)

print it.getxref()
items = it.modules.items()
items.sort()
for k,v in items:
    print k, v
for k,v in it.warnings.items():
    print k,v
for k in dir(it):
    print k
for k in it.path:
    print k
