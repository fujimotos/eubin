bindir = /usr/local/bin

VERSION = v1.2.2
COMPILE = tools/compile.py
PYTHON = /usr/bin/env python3

all: build/eubin

build/eubin: eubin/*.py
	mkdir -p build
	$(COMPILE) -o build/eubin
	chmod +x build/eubin

clean:
	rm -f build/eubin

install:
	install -m 755 build/eubin $(bindir)/eubin

uninstall:
	rm $(bindir)/eubin

archive:
	git archive --prefix eubin-${VERSION}/ ${VERSION} \
      | gzip -9 > eubin-$(VERSION).tar.gz

test:
	$(PYTHON) -m unittest discover -b -v test

.PHONY: all clean install uninstall test
