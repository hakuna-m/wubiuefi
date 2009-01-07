all: build

build: wubi

wubi: check_wine pylauncher src/main.py src/wubi/*.py
	rm -rf build/wubi
	cp wine/drive_c/windows/system32/python23.dll build/pylauncher #TBD
	PYTHONPATH=src tools/pywine -OO build/pylauncher/pack.py src/main.py build/wubi data bin
	mv build/wubi/application.exe build/wubi.exe

wubizip: check_wine pylauncher src/main.py src/wubi/*.py
	rm -rf build/wubi
	cp wine/drive_c/windows/system32/python23.dll build/pylauncher #TBD
	PYTHONPATH=src tools/pywine build/pylauncher/pack.py src/main.py --nopyc build/wubi data bin
	cp wine/drive_c/Python23/python.exe build/wubi/files #TBD
	mv build/wubi/files build/wubi/wubi-app
	cd build/wubi; zip -r ../wubi-app.zip wubi-app
	mv build/wubi/wubi-app build/wubi/files

pylauncher: 7z src/pylauncher/*.c src/pylauncher/*.py
	cp -rf src/pylauncher build
	cd build/pylauncher; make

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
