prefix = /usr/local
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin

COMPILE = tools/compile.py

all: build/eubin

build/eubin:
	mkdir -p build
	$(COMPILE) -o build/eubin

clean:
	rm -f build/eubin

install:
	install -m 755 build/eubin $(bindir)/eubin

uninstall:
	rm $(bindir)/eubin

.PHONY: all clean install uninstall
