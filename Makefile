PYTHON = python
PYWINE = tools/pywine

all: build

build: build_with_cx_freeze

build_with_pyinstaller:
	rm -rf dist
	mkdir -p dist
	tools/pyinstaller_build pyinstaller.spec

build_with_cx_freeze:
	rm -rf build
	mkdir -p build/wubi
	tools/wine c:/cx_freeze/FreezePython.exe -OO --include-path src --install-dir build/wubi --base-binary Win32GUI src/wubi/wubi.py
	cp -a bin build/wubi
	cp -a data build/wubi
	cp -a winboot build/wubi
	cd build;7z a -t7z -m0=lzma -mx=9 -mfb=256 -md=32m -ms=on wubi.7z wubi
	echo ';!@Install@!UTF-8!\nTitle="Wubi, Windows Ubuntu Installer"\nRunProgram="wubi\wubi.exe "\n;!@InstallEnd@!'> build/7z.conf
	cat src/selfextract/7zS.sfx build/7z.conf build/wubi.7z > build/wubi.exe

test: build/wubi.exe
	tools/wine build/wubi.exe -v

unittest:
	$(pywine) tools/test

run:
	PYTHONPATH=src $(PYWINE) src/wubi/wubi.py -v

clean:
	rm -rf dist
	rm -rf build
	rm -rf buildpyinstaller

.PHONY: all build test
