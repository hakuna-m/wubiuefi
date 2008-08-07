PYTHON = tools/pywine

all: build

build:
	$(PYTHON) setup.py build_ext -i

test: build
	$(PYTHON) tools/test

try: 
	$(PYTHON) wubi/wubi.py

.PHONY: all build test
