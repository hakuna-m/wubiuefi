PYTHON = python
PYWINE = tools/pywine

all: build

build:
	$(PYTHON) setup.py build_ext -i

test: build
	$(PYTHON) tools/test

run_win32:
	$(PYWINE) wubi/wubi.py -v

.PHONY: all build test
