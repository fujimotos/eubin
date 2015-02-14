Eubin
=====

Eubin (pronounced as 'you-bin') is a POP3 client with bare
minimum features. The aim of this program is to allow users
to fetch messages from the remote mailbox as easy as possible.

Requirements
------------

Python 3.3 or later.

Installation
------------

1. Run makedist.py to get a single-file executable.

    $ ./makedist.py

2. Put the executable in somewhere under your `$PATH`.

    $ mv dist/eubin /path/to/install/

Configuring
-----------

Eubin will search `$HOME/.eubin/` for configuration files.
The name of configuration files can be anything as long as
the extension is `.conf`.

Each config file holds the settings for an email account.
For example, If you have two email accounts, one for work
and one for personal use, you will have two config files:

    $HOME/
    └─.eubin/
      ├─ personal@mydomain.com.conf
      └─ work@mydomain.com.conf

There is a sample configuration file in the github repository
that can be used as starting point.

    $ cp sample/sample@gmail.net.conf ~/.eubin/personal@mydomain.com.conf
    $ vi ~/.eubin/personal@mydomain.com.conf
