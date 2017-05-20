eubin
=====

`eubin` is a humble mail retriever. It fetches emails from a remote mail
server (like pop.gmail.com) and delivers them to the local drive for you.

The scope of this program is limited and protocol support is minimal.
Also there is no plan for it to creep some funky new features. But,
look and behold, this piece of software does its job very well.

Personally, I've been using `eubin` for years in several environments,
and it served me very diligently so far. I will happily use this program
till the entire email culture dies out.

Feature
-------

### Limitations

 * Only support Python 3.4 (or later)
 * Only support POP3
 * Only support Maildir

### Some nice things

*Small system footprint*

 * The whole program is a single-file binary with ~~9kb in size.~~  
    * As of v1.2.1, it's roughly *4kb* in size (thanks to the glorious zip
      compression).
 * So you can purge the software in a heartbeat if you find it useless.

*Sane TLS support*

 * Encryption is hard.
 * Eubin solves this problem by simply delegating to `ssl.create_default_context()`.
 * This should provide you not-so-much-terrible cryptographic choices.

*Healthy password management*

 * It can integrate with many password managers via `pass_eval` directive.
 * So you can avoid storing the password in plaintext.

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

Also you might want to clean up the config directory:

    $ rm -r ~/.eubin
