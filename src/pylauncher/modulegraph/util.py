import os
import imp
import sys

def imp_find_module(name, path=None):
    """
    same as imp.find_module, but handles dotted names
    """
    names = name.split('.')
    if path is not None:
        path = [os.path.realpath(path)]
    for name in names:
        result = imp.find_module(name, path)
        path = [result[1]]
    return result

def _check_importer_for_path(name, path_item):
    try:
        importer = sys.path_importer_cache[path_item]
    except KeyError:
        for path_hook in sys.path_hooks:
            try:
                importer = path_hook(path_item)
                break
            except ImportError:
                pass
        else:
            importer = None
        sys.path_importer_cache.setdefault(path_item, importer)

    if importer is None:
        try:
            return imp.find_module(name, [path_item])
        except ImportError:
            return None
    return importer.find_module(name)

def imp_walk(name):
    """
    yields namepart, tuple_or_importer for each path item

    raise ImportError if a name can not be found.
    """
    if name in sys.builtin_module_names:
        yield name, (None, None, ("", "", imp.C_BUILTIN))
        return
    paths = sys.path
    res = None
    for namepart in name.split('.'):
        for path_item in paths:
            res = _check_importer_for_path(namepart, path_item)
            if hasattr(res, 'find_module'):
                break
        else:
            break
        yield namepart, res
        paths = [os.path.join(path_item, namepart)]
    else:
        return
    raise ImportError('No module named %s' % (name,))


def test_imp_find_module():
    import encodings.aliases
    fn = imp_find_module('encodings.aliases')[1]
    assert encodings.aliases.__file__.startswith(fn)

def test_imp_walk():
    import encodings.aliases
    imps = list(imp_walk('encodings.aliases'))
    assert len(imps) == 2

    assert imps[0][0] == 'encodings'
    assert encodings.__file__.startswith(imps[0][1][1])

    assert imps[1][0] == 'aliases'
    assert encodings.aliases.__file__.startswith(imps[1][1][1])
        

if __name__ == '__main__':
    test_imp_find_module()
    test_imp_walk()
