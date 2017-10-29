eubin
=====

`eubin` is a tiny mail retriever. It connects to a remote POP3 server
(like pop.gmail.com) and retrieves your emails to the local drive.

### Features

*Small system footprint*

 * The whole executable is a single-file binary with 4kb in size.

*Sane TLS support*

 * Eubin delegates the cipher choice to `ssl.create_default_context()`.
 * This should provide moderate, predicatable security settings.

*Easy Password Manager Integration*

 * Eubin integrates well with many password managers via `pass_eval` directive.

### Limitations

 * Support Python 3.4 (or later)
 * Only support POP3
 * Only support Maildir


How to install
--------------

Clone the repository and run "make" and "make install".

    $ git clone https://github.com/fujimotos/eubin.git
    $ cd eubin
    $ make
    $ sudo make install


Settings
--------

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
dest = ~/mail/
leavecopy = yes  # Leave a copy of mails on remote server.
leavemax =       # Number of mails to leave (Leave blank to never delete).
timeout = 600    # (sec)

[security]
apop = no
overssl = yes
starttls = no
```

Then create a mail directory to store your emails:

    $ mkdir -p ~/mail/{cur,new,tmp}


Usage
-----

1) run eubin

    $ eubin

2) display the list of command line options:

    $ eubin --help

To run eubin periodically, add the following line to cron:

    */5 * * * * /usr/local/bin/eubin --quiet


Uninstallation
--------------

Eubin is a single-file executable. So you can uninstall the program cleanly
by just removing it:

    $ sudo rm /usr/local/bin/eubin

Also you might want to clean up the configuration directory:

    $ rm -r ~/.eubin
