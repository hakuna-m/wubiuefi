"""
Find modules used by a script, using bytecode analysis.

Based on the stdlib modulefinder by Thomas Heller and Just van Rossum,
but uses a graph data structure and 2.3 features
"""

#from pkg_resources import require
#require("altgraph")

import pkg_resources
import StringIO
import dis
import imp
import marshal
import os
import sys
import new
import struct
import urllib
import zipfile
import zipimport

from altgraph.Dot import Dot
from altgraph.ObjectGraph import ObjectGraph
from altgraph.GraphUtil import filter_stack
from altgraph.compat import *

import util

READ_MODE = "U"  # universal line endings

# Modulegraph does a good job at simulating Python's, but it can not
# handle packagepath modifications packages make at runtime.  Therefore there
# is a mechanism whereby you can register extra paths in this map for a
# package, and it will be honored.

# Note this is a mapping is lists of paths.
packagePathMap = {}


def namespace_package_path(fqname, pathname, syspath=None):
    path = []

    if syspath is None:
        working_set = pkg_resources.working_set
    else:
        working_set = pkg_resources.WorkingSet(syspath)

    for dist in working_set:
        assert dist in working_set

        if dist.has_metadata('namespace_packages.txt'):
            namespaces = dist.get_metadata(
                    'namespace_packages.txt').splitlines()
            if fqname in namespaces:
                path.append(os.path.join(dist.location, *fqname.split('.')))

    if not path:
        return [pathname]

    else:
        return path

def os_listdir(path):
    """
    os.listdir with support for zipfiles
    """
    try:
        return os.listdir(path)
    except os.error:
        info = sys.exc_info()

        rest = ''
        while not os.path.exists(path):
            path, r = os.path.split(path)
            rest = os.path.join(r, rest)

        if not os.path.isfile(path):
            # Directory really doesn't exist
            raise info[0], info[1], info[2]

        try:
            zf = zipfile.ZipFile(path)
        except zipfile.BadZipfile:
            raise info[0], info[1], info[2]

        if rest:
            rest = rest + '/'
        result = set()
        for nm in zf.namelist():
            if nm.startswith(rest):
                result.add(nm[len(rest):].split('/')[0])
        return list(result)


def _code_to_file(co):
    """ Convert code object to a .pyc pseudo-file """
    return StringIO.StringIO(
            imp.get_magic() + chr(0)*4 + marshal.dumps(co))

def find_module(name, path=None):
    """
    A version of imp.find_module that works with zipped packages.
    """
    if path is None:
        path = sys.path

    for entry in path:
        importer = pkg_resources.get_importer(entry)
        loader = importer.find_module(name)
        if loader is None: continue

        if isinstance(importer, pkg_resources.ImpWrapper):
            filename = loader.filename
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                fp = open(filename, 'rb')
                description = ('.pyc', 'rb', imp.PY_COMPILED)
                return (fp, filename, description)

            elif filename.endswith('.py'):
                fp = file(filename, READ_MODE)
                description = ('.py', READ_MODE, imp.PY_SOURCE)
                return (fp, filename, description)

            else:
                for _sfx, _mode, _type in imp.get_suffixes():
                    if _type == imp.C_EXTENSION and filename.endswith(_sfx):
                        description = (_sfx, 'rb', imp.C_EXTENSION)
                        break
                else:
                    description = ('', '', imp.PKG_DIRECTORY)

                return (None, filename, description)

        elif hasattr(loader, 'get_code'):
            co = loader.get_code(name)
            fp = _code_to_file(co)

        pathname = os.path.join(entry, *name.split('.'))

        if isinstance(loader, zipimport.zipimporter):
            # Check if this happens to be a wrapper module introduced by setuptools,
            # if it is we return the actual extension.
            zn = '/'.join(name.split('.'))
            for _sfx, _mode, _type in imp.get_suffixes():
                if _type == imp.C_EXTENSION:
                    p = loader.prefix + zn + _sfx
                    if p in loader._files:
                        description = (_sfx, 'rb', imp.C_EXTENSION)
                        return (None, pathname + _sfx, description)

        if hasattr(loader, 'is_package') and loader.is_package(name):
            return (None, pathname, ('', '', imp.PKG_DIRECTORY))

        pathname = pathname + '.pyc'
        description = ('.pyc', 'rb', imp.PY_COMPILED)
        return (fp, pathname, description)

    raise ImportError(name)

def moduleInfoForPath(path, suffixes=imp.get_suffixes()):
    for (ext, readmode, typ) in imp.get_suffixes():
        if path.endswith(ext):
            return os.path.basename(path)[:-len(ext)], readmode, typ
    return None

# A Public interface
def AddPackagePath(packagename, path):
    paths = packagePathMap.get(packagename, [])
    paths.append(path)
    packagePathMap[packagename] = paths

replacePackageMap = {}

# This ReplacePackage mechanism allows modulefinder to work around the
# way the _xmlplus package injects itself under the name "xml" into
# sys.modules at runtime by calling ReplacePackage("_xmlplus", "xml")
# before running ModuleGraph.

def ReplacePackage(oldname, newname):
    replacePackageMap[oldname] = newname

class Node(object):
    def __init__(self, identifier):
        self.graphident = identifier
        self.identifier = identifier
        self.namespace = {}
        self.filename = None
        self.packagepath = None
        self.code = None
        # The set of global names that are assigned to in the module.
        # This includes those names imported through starimports of
        # Python modules.
        self.globalnames = set()
        # The set of starimports this module did that could not be
        # resolved, ie. a starimport from a non-Python module.
        self.starimports = set()

    def __contains__(self, name):
        return name in self.namespace

    def __getitem__(self, name):
        return self.namespace[name]

    def __setitem__(self, name, value):
        self.namespace[name] = value

    def get(self, *args):
        return self.namespace.get(*args)

    def __cmp__(self, other):
        return cmp(self.graphident, other.graphident)

    def __hash__(self):
        return hash(self.graphident)

    def infoTuple(self):
        return (self.identifier,)

    def __repr__(self):
        return '%s%r' % (type(self).__name__, self.infoTuple())

class Alias(str):
    pass

class AliasNode(Node):
    def __init__(self, name, node):
        super(AliasNode, self).__init__(name)
        for k in 'identifier', 'packagepath', 'namespace', 'globalnames', 'startimports':
            setattr(self, k, getattr(node, k, None))

    def infoTuple(self):
        return (self.graphident, self.identifier)

class BadModule(Node):
    pass

class ExcludedModule(BadModule):
    pass

class MissingModule(BadModule):
    pass

class Script(Node):
    def __init__(self, filename):
        super(Script, self).__init__(filename)
        self.filename = filename

    def infoTuple(self):
        return (self.filename,)

class BaseModule(Node):
    def __init__(self, name, filename=None, path=None):
        super(BaseModule, self).__init__(name)
        self.filename = filename
        self.packagepath = path

    def infoTuple(self):
        return tuple(filter(None, (self.identifier, self.filename, self.packagepath)))

class BuiltinModule(BaseModule):
    pass

class SourceModule(BaseModule):
    pass

class CompiledModule(BaseModule):
    pass

class Package(BaseModule):
    pass

class FlatPackage(BaseModule):
    pass

class Extension(BaseModule):
    pass

class ArchiveModule(BaseModule):
    pass

class ModuleGraph(ObjectGraph):
    def __init__(self, path=None, excludes=(), replace_paths=(), implies=(), graph=None, debug=0):
        super(ModuleGraph, self).__init__(graph=graph, debug=debug)
        if path is None:
            path = sys.path
        self.path = path
        self.lazynodes = {}
        # excludes is stronger than implies
        self.lazynodes.update(dict(implies))
        for m in excludes:
            self.lazynodes[m] = None
        self.replace_paths = replace_paths

    def implyNodeReference(self, node, other):
        """
        Imply that one node depends on another.
        other may be a module name or another node.

        For use by extension modules and tricky import code
        """
        if not isinstance(other, Node):
            if not isinstance(other, tuple):
                other = (other, node)
            others = self.import_hook(*other)
            for other in others:
                self.createReference(node, other)
        elif isinstance(other, AliasNode):
            self.addNode(other)
            other.connectTo(node)
        else:
            self.createReference(node, other)


    def createReference(self, fromnode, tonode, edge_data='direct'):
        """
        Create a reference from fromnode to tonode
        """
        return super(ModuleGraph, self).createReference(fromnode, tonode, edge_data=edge_data)

    def findNode(self, name):
        """
        Find a node by identifier.  If a node by that identifier exists,
        it will be returned.

        If a lazy node exists by that identifier with no dependencies (excluded),
        it will be instantiated and returned.

        If a lazy node exists by that identifier with dependencies, it and its
        dependencies will be instantiated and scanned for additional dependencies.
        """
        data = super(ModuleGraph, self).findNode(name)
        if data is not None:
            return data
        if name in self.lazynodes:
            deps = self.lazynodes.pop(name)
            if deps is None:
                # excluded module
                m = self.createNode(ExcludedModule, name)
            elif isinstance(deps, Alias):
                other = self._safe_import_hook(deps, None, None).pop()
                m = self.createNode(AliasNode, name, other)
                self.implyNodeReference(m, other)
            else:
                m = self._safe_import_hook(name, None, None).pop()
                for dep in deps:
                    self.implyNodeReference(m, dep)
            return m
        return None

    def run_script(self, pathname, caller=None):
        """
        Create a node by path (not module name).  It is expected to be a Python
        source file, and will be scanned for dependencies.
        """
        self.msg(2, "run_script", pathname)
        pathname = os.path.realpath(pathname)
        m = self.findNode(pathname)
        if m is not None:
            return m

        co = compile(file(pathname, READ_MODE).read()+'\n', pathname, 'exec')
        if self.replace_paths:
            co = self.replace_paths_in_code(co)
        m = self.createNode(Script, pathname)
        m.code = co
        self.createReference(caller, m)
        self.scan_code(co, m)
        return m

    def import_hook(self, name, caller=None, fromlist=None):
        """
        Import a module

        Return the set of modules that are imported
        """
        self.msg(3, "import_hook", name, caller, fromlist)
        parent = self.determine_parent(caller)
        q, tail = self.find_head_package(parent, name)
        m = self.load_tail(q, tail)
        modules = set([m])
        if fromlist and m.packagepath:
            modules.update(self.ensure_fromlist(m, fromlist))
        for m in modules:
            self.createReference(caller, m)
        return modules

    def determine_parent(self, caller):
        """
        Determine the package containing a node
        """
        self.msgin(4, "determine_parent", caller)
        parent = None
        if caller:
            pname = caller.identifier
            if caller.packagepath:
                parent = self.findNode(pname)
            elif '.' in pname:
                pname = pname[:pname.rfind('.')]
                parent = self.findNode(pname)
        self.msgout(4, "determine_parent ->", parent)
        return parent

    def find_head_package(self, parent, name):
        """
        Given a calling parent package and an import name determine the containing
        package for the name
        """
        self.msgin(4, "find_head_package", parent, name)
        if '.' in name:
            head, tail = name.split('.', 1)
        else:
            head, tail = name, ''
        if parent:
            qname = parent.identifier + '.' + head
        else:
            qname = head
        q = self.import_module(head, qname, parent)
        if q:
            self.msgout(4, "find_head_package ->", (q, tail))
            return q, tail
        if parent:
            qname = head
            parent = None
            q = self.import_module(head, qname, parent)
            if q:
                self.msgout(4, "find_head_package ->", (q, tail))
                return q, tail
        self.msgout(4, "raise ImportError: No module named", qname)
        raise ImportError, "No module named " + qname

    def load_tail(self, q, tail):
        self.msgin(4, "load_tail", q, tail)
        m = q
        while tail:
            i = tail.find('.')
            if i < 0: i = len(tail)
            head, tail = tail[:i], tail[i+1:]
            mname = "%s.%s" % (m.identifier, head)
            m = self.import_module(head, mname, m)
            if not m:
                self.msgout(4, "raise ImportError: No module named", mname)
                raise ImportError, "No module named " + mname
        self.msgout(4, "load_tail ->", m)
        return m

    def ensure_fromlist(self, m, fromlist):
        fromlist = set(fromlist)
        self.msg(4, "ensure_fromlist", m, fromlist)
        if '*' in fromlist:
            fromlist.update(self.find_all_submodules(m))
            fromlist.remove('*')
        for sub in fromlist:
            submod = m.get(sub)
            if submod is None:
                fullname = m.identifier + '.' + sub
                submod = self.import_module(sub, fullname, m)
                if submod is None:
                    raise ImportError, "No module named " + fullname
            yield submod

    def find_all_submodules(self, m):
        if not m.packagepath:
            return
        # 'suffixes' used to be a list hardcoded to [".py", ".pyc", ".pyo"].
        # But we must also collect Python extension modules - although
        # we cannot separate normal dlls from Python extensions.
        suffixes = [triple[0] for triple in imp.get_suffixes()]
        for path in m.packagepath:
            try:
                names = os_listdir(path)
            except os.error:
                self.msg(2, "can't list directory", path)
                continue
            for (path, mode, typ) in ifilter(None, imap(moduleInfoForPath, names)):
                if path != '__init__':
                    yield path

    def import_module(self, partname, fqname, parent):
        self.msgin(3, "import_module", partname, fqname, parent)
        m = self.findNode(fqname)
        if m is not None:
            self.msgout(3, "import_module ->", m)
            if parent:
                self.createReference(m, parent)
            return m
        if parent and parent.packagepath is None:
            self.msgout(3, "import_module -> None")
            return None
        try:
            fp, pathname, stuff = self.find_module(partname,
                parent and parent.packagepath, parent)
        except ImportError:
            self.msgout(3, "import_module ->", None)
            return None

        m = self.load_module(fqname, fp, pathname, stuff)
        if parent:
            self.createReference(m, parent)
            parent[partname] = m
        self.msgout(3, "import_module ->", m)
        return m

    def load_module(self, fqname, fp, pathname, (suffix, mode, typ)):
        self.msgin(2, "load_module", fqname, fp and "fp", pathname)
        if typ == imp.PKG_DIRECTORY:
            m = self.load_package(fqname, pathname)
            self.msgout(2, "load_module ->", m)
            return m
        if typ == imp.PY_SOURCE:
            co = compile(fp.read() + '\n', pathname, 'exec')
            cls = SourceModule
        elif typ == imp.PY_COMPILED:
            if fp.read(4) != imp.get_magic():
                self.msgout(2, "raise ImportError: Bad magic number", pathname)
                raise ImportError, "Bad magic number in %s" % pathname
            fp.read(4)
            co = marshal.loads(fp.read())
            cls = CompiledModule
        elif typ == imp.C_BUILTIN:
            cls = BuiltinModule
            co = None
        else:
            cls = Extension
            co = None
        m = self.createNode(cls, fqname)
        m.filename = pathname
        if co:
            if self.replace_paths:
                co = self.replace_paths_in_code(co)
            m.code = co
            self.scan_code(co, m)
        self.msgout(2, "load_module ->", m)
        return m

    def _safe_import_hook(self, name, caller, fromlist):
        # wrapper for self.import_hook() that won't raise ImportError
        try:
            mods = self.import_hook(name, caller)
        except ImportError, msg:
            self.msg(2, "ImportError:", str(msg))
            m = self.createNode(MissingModule, name)
            self.createReference(caller, m)
        else:
            assert len(mods) == 1
            m = list(mods)[0]

        subs = set([m])
        for sub in (fromlist or ()):
            # If this name is in the module namespace already,
            # then add the entry to the list of substitutions
            if sub in m:
                sm = m[sub]
                if sm is not None:
                    subs.add(sm)
                continue

            # See if we can load it
            fullname = name + '.' + sub
            sm = self.findNode(fullname)
            if sm is None:
                try:
                    sm = self.import_hook(name, caller, [sub])
                except ImportError, msg:
                    self.msg(2, "ImportError:", str(msg))
                    sm = self.createNode(MissingModule, fullname)
                else:
                    sm = self.findNode(fullname)

            m[sub] = sm
            if sm is not None:
                self.createReference(sm, m)
                subs.add(sm)
        return subs

    def scan_code(self, co, m,
            HAVE_ARGUMENT=chr(dis.HAVE_ARGUMENT),
            LOAD_CONST=chr(dis.opname.index('LOAD_CONST')),
            IMPORT_NAME=chr(dis.opname.index('IMPORT_NAME')),
            STORE_NAME=chr(dis.opname.index('STORE_NAME')),
            STORE_GLOBAL=chr(dis.opname.index('STORE_GLOBAL')),
            unpack=struct.unpack):
        code = co.co_code
        constants = co.co_consts
        n = len(code)
        i = 0
        fromlist = None
        while i < n:
            c = code[i]
            i += 1
            if c >= HAVE_ARGUMENT:
                i = i+2
            if c == LOAD_CONST:
                # An IMPORT_NAME is always preceded by a LOAD_CONST, it's
                # a tuple of "from" names, or None for a regular import.
                # The tuple may contain "*" for "from <mod> import *"
                oparg = unpack('<H', code[i - 2:i])[0]
                fromlist = co.co_consts[oparg]
            elif c == IMPORT_NAME:
                assert fromlist is None or type(fromlist) is tuple
                oparg = unpack('<H', code[i - 2:i])[0]
                name = co.co_names[oparg]
                have_star = False
                if fromlist is not None:
                    fromlist = set(fromlist)
                    if '*' in fromlist:
                        fromlist.remove('*')
                        have_star = True
                self._safe_import_hook(name, m, fromlist)
                if have_star:
                    # We've encountered an "import *". If it is a Python module,
                    # the code has already been parsed and we can suck out the
                    # global names.
                    mm = None
                    if m.packagepath:
                        # At this point we don't know whether 'name' is a
                        # submodule of 'm' or a global module. Let's just try
                        # the full name first.
                        mm = self.findNode(m.identifier + '.' + name)
                    if mm is None:
                        mm = self.findNode(name)
                    if mm is not None:
                        m.globalnames.update(mm.globalnames)
                        m.starimports.update(mm.starimports)
                        if mm.code is None:
                            m.starimports.add(name)
                    else:
                        m.starimports.add(name)
            elif c == STORE_NAME or c == STORE_GLOBAL:
                # keep track of all global names that are assigned to
                oparg = unpack('<H', code[i - 2:i])[0]
                name = co.co_names[oparg]
                m.globalnames.add(name)
        cotype = type(co)
        for c in constants:
            if isinstance(c, cotype):
                self.scan_code(c, m)

    def load_package(self, fqname, pathname):
        """
        Called only when an imp.PACKAGE_DIRECTORY is found
        """
        self.msgin(2, "load_package", fqname, pathname)
        newname = replacePackageMap.get(fqname)
        if newname:
            fqname = newname
        m = self.createNode(Package, fqname)
        m.filename = pathname
        m.packagepath = namespace_package_path(fqname, pathname)

        # As per comment at top of file, simulate runtime packagepath additions.
        m.packagepath = m.packagepath + packagePathMap.get(fqname, [])



        fp, buf, stuff = self.find_module("__init__", m.packagepath)
        self.load_module(fqname, fp, buf, stuff)
        self.msgout(2, "load_package ->", m)
        return m

    def find_module(self, name, path, parent=None):
        if parent is not None:
            # assert path is not None
            fullname = parent.identifier + '.' + name
        else:
            fullname = name

        node = self.findNode(fullname)
        if node is not None:
            self.msgout(3, "find_module -> already included?", node)
            raise ImportError, name

        if path is None:
            if name in sys.builtin_module_names:
                return (None, None, ("", "", imp.C_BUILTIN))

            path = self.path

        fp, buf, stuff = find_module(name, path)
        if buf:
            buf = os.path.realpath(buf)
        return (fp, buf, stuff)

    def create_xref(self, out=None):
        if out is None:
            out = sys.stdout
        scripts = []
        mods = []
        for mod in self.flatten():
            name = os.path.basename(mod.identifier)
            if isinstance(mod, Script):
                scripts.append((name, mod))
            else:
                mods.append((name, mod))
        scripts.sort()
        mods.sort()
        scriptnames = [name for name, m in scripts]
        scripts.extend(mods)
        mods = scripts

        title = "modulegraph cross reference for "  + ', '.join(scriptnames)
        print >>out, """<html><head><title>%s</title></head>
            <body><h1>%s</h1>""" % (title, title)

        def sorted_namelist(mods):
            lst = [os.path.basename(mod.identifier) for mod in mods if mod]
            lst.sort()
            return lst
        for name, m in mods:
            if isinstance(m, BuiltinModule):
                print >>out, """<a name="%s" /><tt>%s</tt>
                    <i>(builtin module)</i> <br />""" % (name, name)
            elif isinstance(m, Extension):
                print >>out, """<a name="%s" /><tt>%s</tt> <tt>%s</tt></a>
                    <br />""" % (name, name, m.filename)
            else:
                url = urllib.pathname2url(m.filename or "")
                print >>out, """<a name="%s" />
                    <a target="code" href="%s" type="text/plain"><tt>%s</tt></a>
                    <br />""" % (name, url, name)
            oute, ince = map(sorted_namelist, self.get_edges(m))
            if oute:
                print >>out, 'imports:'
                for n in oute:
                    print >>out, """<a href="#%s">%s</a>""" % (n, n)
                print >>out, '<br />'
            if ince:
                print >>out, 'imported by:'
                for n in ince:
                    print >>out, """<a href="#%s">%s</a>""" % (n, n)
                print >>out, '<br />'
            print >>out, '<br/>'
        print >>out, '</body></html>'


    def itergraphreport(self, name='G', flatpackages=()):
        nodes = map(self.graph.describe_node, self.graph.iterdfs(self))
        describe_edge = self.graph.describe_edge
        edges = deque()
        packagenodes = set()
        packageidents = {}
        nodetoident = {}
        inpackages = {}
        mainedges = set()

        # XXX - implement
        flatpackages = dict(flatpackages)

        def nodevisitor(node, data, outgoing, incoming):
            if not isinstance(data, Node):
                return {'label': str(node)}
            #if isinstance(d, (ExcludedModule, MissingModule, BadModule)):
            #    return None
            s = '<f0> ' + type(data).__name__
            for i,v in izip(count(1), data.infoTuple()[:1]):
                s += '| <f%d> %s' % (i,v)
            return {'label':s, 'shape':'record'}

        def edgevisitor(edge, data, head, tail):
            if data == 'orphan':
                return {'style':'dashed'}
            elif data == 'pkgref':
                return {'style':'dotted'}
            return {}

        yield 'digraph %s {\n' % (name,)
        attr = dict(rankdir='LR', concentrate='true')
        cpatt  = '%s="%s"'
        for item in attr.iteritems():
            yield '\t%s;\n' % (cpatt % item,)

        # find all packages (subgraphs)
        for (node, data, outgoing, incoming) in nodes:
            nodetoident[node] = getattr(data, 'identifier', None)
            if isinstance(data, Package):
                packageidents[data.identifier] = node
                inpackages[node] = set([node])
                packagenodes.add(node)


        # create sets for subgraph, write out descriptions
        for (node, data, outgoing, incoming) in nodes:
            # update edges
            for edge in imap(describe_edge, outgoing):
                edges.append(edge)

            # describe node
            yield '\t"%s" [%s];\n' % (
                node,
                ','.join([
                    (cpatt % item) for item in
                    nodevisitor(node, data, outgoing, incoming).iteritems()
                ]),
            )

            inside = inpackages.get(node)
            if inside is None:
                inside = inpackages[node] = set()
            ident = nodetoident[node]
            if ident is None:
                continue
            pkgnode = packageidents.get(ident[:ident.rfind('.')])
            if pkgnode is not None:
                inside.add(pkgnode)


        graph = []
        subgraphs = {}
        for key in packagenodes:
            subgraphs[key] = []

        while edges:
            edge, data, head, tail = edges.popleft()
            if ((head, tail)) in mainedges:
                continue
            mainedges.add((head, tail))
            tailpkgs = inpackages[tail]
            common = inpackages[head] & tailpkgs
            if not common and tailpkgs:
                usepkgs = sorted(tailpkgs)
                if len(usepkgs) != 1 or usepkgs[0] != tail:
                    edges.append((edge, data, head, usepkgs[0]))
                    edges.append((edge, 'pkgref', usepkgs[-1], tail))
                    continue
            if common:
                common = common.pop()
                if tail == common:
                    edges.append((edge, data, tail, head))
                elif head == common:
                    subgraphs[common].append((edge, 'pkgref', head, tail))
                else:
                    edges.append((edge, data, common, head))
                    edges.append((edge, data, common, tail))

            else:
                graph.append((edge, data, head, tail))

        def do_graph(edges, tabs):
            edgestr = tabs + '"%s" -> "%s" [%s];\n'
            # describe edge
            for (edge, data, head, tail) in edges:
                attribs = edgevisitor(edge, data, head, tail)
                yield edgestr % (
                    head,
                    tail,
                    ','.join([(cpatt % item) for item in attribs.iteritems()]),
                )

        for g, edges in subgraphs.iteritems():
            yield '\tsubgraph "cluster_%s" {\n' % (g,)
            yield '\t\tlabel="%s";\n' % (nodetoident[g],)
            for s in do_graph(edges, '\t\t'):
                yield s
            yield '\t}\n'

        for s in do_graph(graph, '\t'):
            yield s

        yield '}\n'

    def graphreport(self, fileobj=None, flatpackages=()):
        if fileobj is None:
            fileobj = sys.stdout
        fileobj.writelines(self.itergraphreport(flatpackages=flatpackages))

    def report(self):
        """Print a report to stdout, listing the found modules with their
        paths, as well as modules that are missing, or seem to be missing.
        """
        print
        print "%-15s %-25s %s" % ("Class", "Name", "File")
        print "%-15s %-25s %s" % ("----", "----", "----")
        # Print modules found
        sorted = [(os.path.basename(mod.identifier), mod) for mod in self.flatten()]
        sorted.sort()
        for (name, m) in sorted:
            print "%-15s %-25s %s" % (type(m).__name__, name, m.filename or "")

    def replace_paths_in_code(self, co):
        new_filename = original_filename = os.path.normpath(co.co_filename)
        for f, r in self.replace_paths:
            f = os.path.join(f, '')
            r = os.path.join(r, '')
            if original_filename.startswith(f):
                new_filename = r + original_filename[len(f):]
                break

        consts = list(co.co_consts)
        for i in range(len(consts)):
            if isinstance(consts[i], type(co)):
                consts[i] = self.replace_paths_in_code(consts[i])

        return new.code(co.co_argcount, co.co_nlocals, co.co_stacksize,
                         co.co_flags, co.co_code, tuple(consts), co.co_names,
                         co.co_varnames, new_filename, co.co_name,
                         co.co_firstlineno, co.co_lnotab,
                         co.co_freevars, co.co_cellvars)

def main():
    # Parse command line
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dgmp:qx:")
    except getopt.error, msg:
        print msg
        return

    # Process options
    debug = 1
    domods = 0
    dodot = False
    addpath = []
    excludes = []
    for o, a in opts:
        if o == '-d':
            debug = debug + 1
        if o == '-m':
            domods = 1
        if o == '-p':
            addpath = addpath + a.split(os.pathsep)
        if o == '-q':
            debug = 0
        if o == '-x':
            excludes.append(a)
        if o == '-g':
            dodot = True

    # Provide default arguments
    if not args:
        script = __file__
    else:
        script = args[0]

    # Set the path based on sys.path and the script directory
    path = sys.path[:]
    path[0] = os.path.dirname(script)
    path = addpath + path
    if debug > 1:
        print "path:"
        for item in path:
            print "   ", repr(item)

    # Create the module finder and turn its crank
    mf = ModuleGraph(path, excludes=excludes, debug=debug)
    for arg in args[1:]:
        if arg == '-m':
            domods = 1
            continue
        if domods:
            if arg[-2:] == '.*':
                mf.import_hook(arg[:-2], None, ["*"])
            else:
                mf.import_hook(arg)
        else:
            mf.run_script(arg)
    mf.run_script(script)
    if dodot:
        mf.graphreport()
    else:
        mf.report()
    return mf  # for -i debugging


if __name__ == '__main__':
    try:
        mf = main()
    except KeyboardInterrupt:
        print "\n[interrupt]"
