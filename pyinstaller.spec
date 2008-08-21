# Pyinstaller build script for Wubi
# http://pyinstaller.python-hosting.com/file/trunk/doc/Manual.html?rev=latest&format=raw#pyinstaller-archives

dist_dir = 'dist'
data_dir = 'data'
bin_dir = 'bin'
exe_name = dist_dir + '\\wubi.exe'
exe_icon = 'data\\images\\Ubuntu.ico'
use_upx = True
strip = False #it may create problems
console = False

extra_modules_paths = [
    'src',
    ]

scripts_to_analyze = [
    os.path.join(HOMEPATH,'support\\_mountzlib.py'),
    os.path.join(HOMEPATH,'support\\useUnicode.py'),
    'src\\wubi\\wubi.py', #must be last
    ]

excluded_binaries = [
    #~ ('_ssl','',''),
    #~ ('_socket','',''),
    #~ ('bz2','',''),
    #~ ('pyexpat','',''),
    #~ ('select','',''),
    #~ ('unicodedata','',''),
    #~ ('pywintypes24.dll','',''),
    #~ ('win32api','',''),
    ]

excluded_modules = [
    #~ ('bdb','',''),
    #~ ('pdb','',''),
    #~ ('unittests','',''),
    #~ ('pydoc','',''),
    ]

# Binaries end up in the root dir accessible via  os.environ['_MEIPASS2']
included_binaries = [
    ('7z.exe', 'bin\\7z.exe', 'BINARY'),
    ('iso.dll', 'bin\\iso.dll', 'BINARY'),
]

analysis = Analysis(scripts_to_analyze, pathex=extra_modules_paths)
scripts = analysis.scripts
binaries = analysis.binaries - excluded_binaries + included_binaries
modules = analysis.pure - excluded_modules

#Let's pack pure modules into a pyz library
pyz = PYZ(modules)

#Let's pack the data
data_tree = Tree(data_dir)
data_pkg = PKG(data_tree, name='data.pkg')

#Let's pack the exe
exe = EXE(
    pyz,
    data_pkg,
    scripts,
    binaries,
    name = exe_name,
    upx = use_upx,
    strip = strip,
    icon = exe_icon,
    console = console ,)

## Another exe wich does not contains binaries and modules
## It requires a separate directory with binaries andmodules
#~ scripts_exe = EXE(
    #~ scripts,
    #~ exclude_binaries = True,
    #~ name = exe_name,
    #~ upx = use_upx,
    #~ icon = exe_icon,
    #~ console = False,)

## A directory containing all the files
all = COLLECT(
    scripts,
    binaries,
    strip = False, #This has to be False or it crashes
    upx = False,
    name = dist_dir + '\\all')

all_modules = COLLECT(
    modules,
    strip = False, #This has to be False or it crashes
    upx = False,
    name = dist_dir + '\\all\\lib')


## A directory containing all the scripts
#~ scripts_dir = COLLECT(
    #~ scripts,
    #~ strip = False, #This has to be False or it crashes
    #~ upx = False,
    #~ name = dist_dir + '\\scripts')

## A directory containing all the scripts
#~ modules_dir = COLLECT(
    #~ modules,
    #~ strip = False, #This has to be False or it crashes
    #~ upx = False,
    #~ name = dist_dir + '\\modules')

## A directory containing all the binaries
#~ binaries_dir = COLLECT(
    #~ binaries,
    #~ strip = False, #This has to be False or it crashes
    #~ upx = False,
    #~ name = dist_dir + LECT(
    #~ binaries,
    #~ strip = False, #This has to be False or it crashes
    #~ upx = False,
    #~ name = dist_dir + '\\binaries')
