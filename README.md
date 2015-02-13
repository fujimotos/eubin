Eubin
=====

Yet another POP3 client.

Requirements
------------

Python 3.3 or later required.

Installation
------------

1. Run makedist.py to get a single-file executable.

  $ ./makedist.py

2. Put the resulting executable in somewhere under your $PATH.

  $ mv dist/eubin /path/to/install/

3. Make the configure directory '.eubin' in your $HOME directory.

  $ mkdir $HOME/.eubin

4. Copy the sample configure file to the directory.
   (Note that the name of config file can be anything, as long as the
    extention is '.conf')

  $ cp sample/sample@gmail.net.conf $HOME/.eubin/myuser@mydomain.com.conf

5. Edit the configure file as you like.

  $ vim $HOME/.eubin/myuser@mydomain.com.conf

6. Run *eubin* to check everything is okay.

  $ eubin
