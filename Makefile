export SHELL = sh
PACKAGE = wubi
REVISION = $(shell bzr revno)
VERSION = $(shell head -n 1 debian/changelog | sed -e "s/^$(PACKAGE) (\(.*\)).*/\1/g")

all: build

build: wubi

wubi: wubi-pre-build
	PYTHONPATH=src tools/pywine -OO build/pylauncher/pack.py --dir=build/wubi src/main.py data build/bin build/version.py build/winboot
	mv build/wubi/application.exe build/wubi.exe

wubizip: wubi-pre-build
	PYTHONPATH=src tools/pywine build/pylauncher/pack.py --dir=build/wubi --nopyc src/main.py data build/bin build/version.py build/winboot
	cp wine/drive_c/Python23/python.exe build/wubi/files #TBD
	cp wine/drive_c/Python23/pythonw.exe build/wubi/files #TBD
	cp build/cpuid/cpuid.dll build/bin
	mv build/wubi/files build/wubi/wubi
	cd build/wubi; zip -r ../wubi.zip wubi
	mv build/wubi/wubi build/wubi/files

wubi-pre-build: check_wine winboot pylauncher src/main.py src/wubi/*.py cpuid version.py
	rm -rf build/wubi
	rm -rf build/bin
	cp -a blobs build/bin
	cp wine/drive_c/windows/system32/python23.dll build/pylauncher #TBD
	cp build/cpuid/cpuid.dll build/bin

version.py:
	$(shell echo 'version = "$(VERSION)"' > build/version.py)
	$(shell echo 'revision = $(REVISION)' >> build/version.py)
	$(shell echo 'application_name = "$(PACKAGE)"' >> build/version.py)

pylauncher: 7z src/pylauncher/*.c src/pylauncher/*.py
	cp -rf src/pylauncher build
	cd build/pylauncher; make

cpuid: src/cpuid/cpuid.c
	cp -rf src/cpuid build
	cd build/cpuid; make

winboot: grub4dos grubutil
	mkdir -p build/winboot
	cp -f data/menu.winboot build/winboot/menu.lst
	cp -f build/grub4dos/stage2/grldr build/winboot/wubildr
	cp -f build/grub4dos/stage2/grub.exe build/winboot/wubildr.exe
	dd if=build/winboot/wubildr of=build/winboot/wubildr.mbr bs=1 count=8192
	cd build/winboot; ../grubutil/grubinst/grubinst -o -b=wubildr wubildr.mbr

grub4dos: src/grub4dos/*
	cp -rf src/grub4dos build
	cd build/grub4dos;./configure --enable-preset-menu=../../data/menu.winboot
	cd build/grub4dos; make

grubutil: src/grubutil/grubinst/*
	cp -rf src/grubutil build
	cd build/grubutil/grubinst; make

# not compiling 7z at the moment, but source is used by pylauncher
7z: src/7z/C/*.c
	cp -rf src/7z build

runbin: wubi
	rm -rf build/test
	mkdir build/test
	cd build/test; ../../tools/wine ../wubi.exe --test

check_wine: tools/check_wine
	tools/check_wine

unittest:
	tools/pywine tools/test

runpy:
	PYTHONPATH=src tools/pywine src/main.py --test

clean:
	rm -rf dist/*
	rm -rf build/*

.PHONY: all build test
