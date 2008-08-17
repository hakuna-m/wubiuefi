PYTHON = python
PYWINE = tools/pywine

all: build

build:
	mkdir -p dist
	tools/pyinstaller_build pyinstaller.spec
#setup.py build_ext -i

test: build
	tools/wine dist/wubi.exe -v

unittest:
	$(pywine) tools/test

run:
	PYTHONPATH=src $(PYWINE) src/wubi/wubi.py -v

clean:
	rm -rf dist

.PHONY: all build test
