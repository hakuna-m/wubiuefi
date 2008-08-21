PYTHON = python
PYWINE = tools/pywine

all: build

build:
	rm -rf dist
	mkdir -p dist
	tools/pyinstaller_build pyinstaller.spec
#setup.py build_ext -i

test: build
	cd dist; ../tools/wine wubi.exe -v

unittest:
	$(pywine) tools/test

run:
	PYTHONPATH=src $(PYWINE) src/wubi/wubi.py -v

clean:
	rm -rf dist
	rm -rf buildpyinstaller

build2:
	rm -rf build
	mkdir -p build/wubi
	cp -a bin/* build/wubi
	cp -a lib build/wubi
	cp src/wubi/wubi.py bild/wubi
	7z a -t7z -m0=lzma -mx=9 -mfb=256 -md=32m -ms=on build/wubi.7z build/wubi
	echo ';!@Install@!UTF-8!\nTitle="Wubi, Windows Ubuntu Installer"\nRunProgram="wubi/wubi.exe "\n;!@InstallEnd@!> build/7z.conf
	cat src/selfextract/7zS.sfx build/7z.conf build/wubi.7z > build/wubi.exe

.PHONY: all build test
