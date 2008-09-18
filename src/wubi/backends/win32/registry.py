import _winreg
import logging
log = logging.getLogger("registry")

def get_value(key, subkey, attr):
    key = getattr(_winreg, key)
    try:
        handle = _winreg.OpenKey(key, subkey)
    except:
        return None
    try:
        (value, type) = _winreg.QueryValueEx(handle, attr)
    except:
        return None
    _winreg.CloseKey(handle)
    return value

def set_value(key, subkey, attr, value):
    key = getattr(_winreg, key)
    try:
        handle = _winreg.OpenKey(key, subkey)
    except:
        handle = _winreg.CreateKey(key, subkey)
    try:
        (value, type) = _winreg.SetValueEx(handle, attr, 0, 1, value)
    except Exception, err:
        log.exception("Cannot set registry key %s\\%s = %s" % (subkey, attr, value), err)
    _winreg.CloseKey(handle)

def delete_key(key, subkey):
    key = getattr(_winreg, key)
    try:
        _winreg.DeleteKey(key, subkey)
    except Exception, err:
        log.exception("Cannot delete registry key %s" % subkey, err)
