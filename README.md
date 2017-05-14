eubin
=====

eubin is a dumb mail retriever which only supports POP3 and Maildir.

**Why eubin?**

 1. Support `pass_eval` option for not storing passwords in plaintext.
 2. Sane SSL handling. It simply delegates SSL settings to
    `ssl.create_default_context()` to avoid stupid mistakes.

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

Configuration
-------------

Eubin will search `$HOME/.eubin/` for configuration files by default.
The name of configuration files can be anything as long as the extension
is `.conf`.

Each file holds the configuration for a single email account. For
example, If you have two email accounts, one for work and one for
personal use, you will have two config files:

    $HOME/
    └─.eubin/
      ├─ personal@mydomain.com.conf
      └─ work@mydomain.com.conf

Here is a full configuration sample:

```INI
[server]
host = pop.gmail.com
port = 995

[account]
user = example@gmail.com
pass = password
# pass_eval = gpg2 --batch -q -d my-password.gpg

[retrieval]
dest = ~/Mail/
leavecopy = yes  # Leave a copy of mails on remote server.
leavemax =       # Number of mails to leave (Leave blank to never delete).
timeout = 600  # (sec)

[security]
apop = no
overssl = yes
starttls = no
```

Uninstallation
--------------

Eubin is a single-file executable. So you can uninstall the program cleanly
by just removing it:

    $ sudo rm /usr/local/bin/eubin

The Makefile also supports 'unintall' directive as well:

    $ sudo make uninstall
