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

.PHONY: all build test
