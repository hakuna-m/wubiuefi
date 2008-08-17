import _winreg

def get_registry_value(key, subkey, attr):
    key = getattr(_winreg, key)
    handle = _winreg.OpenKey(key, subkey)
    try:
        (value, type) = _winreg.QueryValueEx(handle, attr)
    except:
        return None
    _winreg.CloseKey(handle)
    return value


