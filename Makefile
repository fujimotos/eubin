prefix = /usr/local
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin

COMPILE = tools/compile.py
PYTHON = /usr/bin/env python3

all: build/eubin

build/eubin: eubin/*.py
	mkdir -p build
	$(COMPILE) -o build/eubin

clean:
	rm -f build/eubin

install:
	install -m 755 build/eubin $(bindir)/eubin

uninstall:
	rm $(bindir)/eubin

test:
	$(PYTHON) -m unittest discover -b -v test

.PHONY: all clean install uninstall test
