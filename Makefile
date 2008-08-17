PYTHON = python
PYWINE = tools/pywine

all: build

build:
	tools/pyinstaller_build pyinstaller.spec
#setup.py build_ext -i

test: build
	tools/wine wubi.exe -v

unittest:
	$(pywine) tools/test

run:
	PYTHONPATH=src $(PYWINE) src/wubi/wubi.py -v

.PHONY: all build test
