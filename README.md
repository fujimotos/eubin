Eubin
=====

Yet another POP3 client.

Requirements
------------

Python 3.3 or later required.

Installation
------------

Run makedist.py to get a single-file executable:

  $ ./makedist.py

Put the executable in somewhere under your $PATH:

  $ mv dist/eubin /path/to/install/

Configuring
-----------

Eubin will search '$HOME/.eubin/' for configuration files.
The name of configuration files can be anything as long as
the extension is '.conf'.

Each config file holds the settings for one email account.
For example, If you have three account 'personal@mydomain.com'
'work@mydomain.com', your will have two config files:

  $HOME/
  └─.eubin/
    ├─ personal@mydomain.com.conf
    └─ work@mydomain.com.conf

There is a sample configuration file in the github repository
that can be used to get started:

  $ cp sample/sample@gmail.net.conf ~/personal@mydomain.com.conf
  $ vi ~/personal@mydomain.com.conf
