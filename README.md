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

There is a sample configuration file in the `sample/` directory
that can be used as starting point.

    $ cp sample/sample@gmail.net.conf ~/.eubin/personal@mydomain.com.conf
    $ vi ~/.eubin/personal@mydomain.com.conf

Additional notes
----------------

My observation is that any POP3 client program should be
bundled with two critical features: *file locking mechanism*
and *careful supports on SSL*.

### 1. File locking

Usually a POP3 agent is scheduled as a cron job and quite a
lot of users run it every minute like this:

    */1 * * * * /usr/local/bin/my-pop3-agent

The problem is that each job can take longer than a minute,
and it can result in two process executing the same agent
program concurrently. This situation often leads to retrieving
the same message again and again.

Yes, it is true that a user can prevent this situation by
using `flock(1)`. But a client program also can solve this
problem by providing built-in file locking mechanism, which
sounds to me like a much saner approach.
