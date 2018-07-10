eubin
=====

Eubin is a small POP3 client. It connects to a remote POP3 server and retrives
messages into your local maildir.

As of v1.2.1, it requires Python 3.4 (or later).

How to install
--------------

Clone the repository and run "make" and "make install".

    $ git clone https://github.com/fujimotos/eubin.git
    $ cd eubin
    $ make
    $ sudo make install

Settings
--------

Eubin searches `$HOME/.eubin/` for configuration files. Each configuration file
should have the suffix `.conf`. Otherwise, it will be ignored.

Each file in the directory holds the configuration for a single email account.
For example, if you have two email accounts, one for work and one for personal
use, you will have two separate configuration files as follows:

    $HOME/
    └─.eubin/
      ├─ personal@mydomain.com.conf
      └─ work@mydomain.com.conf

Here is a full configuration example:

```INI
[server]
host = pop.gmail.com
port = 995

[account]
user = example@gmail.com
pass = password
# pass_eval = gpg2 --batch -q -d my-password.gpg

[retrieval]
dest = ~/mail/
leavecopy = yes  # Leave a copy of mails on remote server.
leavemax =       # Number of mails to leave (Leave blank to never delete).
timeout = 600    # (sec)

[security]
apop = no
overssl = yes
starttls = no
```

You need to create the target mail directory before running eubin.

    $ mkdir -p ~/mail/{cur,new,tmp}

Usage
-----

Just run the `eubin` command to retrieve mails:

    $ eubin

To run eubin periodically, add the following line to cron:

    */5 * * * * /usr/local/bin/eubin -q

How to uninstall
----------------

Eubin is a single-file executable. So you can uninstall eubin cleanly just by
removing the executable from your PATH.

    $ sudo rm /usr/local/bin/eubin

Also you might want to remove the configuration directory:

    $ rm -r ~/.eubin
