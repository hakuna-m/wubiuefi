#http://pyinstaller.python-hosting.com/file/trunk/doc/Manual.html?rev=latest&format=raw#pyinstaller-archives

a = Analysis([
    os.path.join(HOMEPATH,'support\\_mountzlib.py'),
    #os.path.join(HOMEPATH,'support\\useUnicode.py'),  #??? why is it needed
    'src\\wubi\\wubi.py'],
    pathex=['src']
    )

exluded_binaries = [
    ('_ssl','',''),
    ('_socket','',''),
    ('bz2','',''),
    ('pyexpat','',''),
    ('select','',''),
    ('unicodedata','',''),
    ('pywintypes24.dll','',''),
    ('win32api','','')]

#Let's pack pure modules into a library
pyz = PYZ(a.pure)

#Let's pack the exe
exe = EXE(
    pyz,
    a.scripts,
    a.binaries - exluded_binaries,
    name="wubi.exe",
    upx=True,
    #~ strip=True, #causes breakage in 2.4
    icon='data\\images\\Ubuntu.ico',
    console=False ,)

    #~ exclude_binaries=False,
    #~ name='wubi.exe',
    #~ debug=False,
    #~ strip=False, #This has to be False or it crashes when 1 exe is used
    #~ upx=True,
    #~ console=False ,
    #~ icon='data\\images\\Ubuntu.ico')

#Another exe wich does not contains binaries
#~ scripts_exe = EXE(
    #~ a.scripts,
    #~ exclude_binaries=True,
    #~ name="wubi.exe",
    #~ upx=False,
    #~ icon='data\\images\\Ubuntu.ico',
    #~ console=False,)

#A folder containing some files
#~ all = COLLECT(
    #~ scripts_exe,
    #~ a.binaries,
    #~ a.pure,
    #~ strip=False, #This has to be False or it crashes
    #~ upx=False,
    #~ name='dist-all')

#~ scripts = COLLECT(
    #~ a.scripts,
    #~ strip=False, #This has to be False or it crashes
    #~ upx=False,
    #~ name='dist-scripts')

#~ pure = COLLECT(
    #~ a.pure,
    #~ strip=False, #This has to be False or it crashes
    #~ upx=False,
    #~ name='dist-pure')

#~ binaries = COLLECT(
    #~ a.binaries - exluded_binaries,
    #~ strip=False, #This has to be False or it crashes
    #~ upx=False,
    #~ name='dist-binaries')
