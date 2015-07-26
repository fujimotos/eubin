Eubin
=====

Eubin (pronounced as 'you-bin') is a POP3 client with bare
minimum features. The aim of this program is to allow users
to fetch messages from the remote mailbox as easy as possible.

Requirements
------------

Python 3.4 or later.

How to install
--------------

Clone the repository and run "make" and "make install".

    $ git clone https://github.com/fujimotos/eubin.git
    $ cd eubin
    $ make
    $ sudo make install

Usage
-----

1) run eubin

    $ eubin

2) display the list of command line options:

    $ eubin --help

To run eubin periodically, add the following line to cron:

    */5 * * * * /usr/local/bin/eubin --quiet

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

There is a sample configuration file in the `sample/` directory
that can be used as starting point.

    $ cp sample/sample@gmail.net.conf ~/.eubin/personal@mydomain.com.conf
    $ vi ~/.eubin/personal@mydomain.com.conf
