CONF_DIR = os.path.expanduser('~/.eubin')
CONF_SUFFIX = '.conf'

LOG_DIR = os.path.join(CONF_DIR, 'log')
LOG_FORMAT = '%(asctime)s\t%(message)s'
LOG_ROTATE = (30, 'd')  # 30 days

def main():
    import getopt, sys

    # Parameter processing
    debug_level = logging.INFO

    opts, args = getopt.getopt(sys.argv[1:], 'v')
    for key, val in opts:
        if key == '-v':
            debug_level -= 10

    # Configure logging
    _log.setLevel(level=debug_level)

    # Main
    for filename, config in get_configs(CONF_DIR, CONF_SUFFIX):
        server, account, retrieval, security = \
            (config[key] for key in ('server', 'account', 'retrieval', 'security'))

        # Setting logging
        logfile = filename.replace(CONF_SUFFIX, '.log')
        handler = logging.handlers.TimedRotatingFileHandler(
            filename = os.path.join(LOG_DIR, logfile),
            interval = LOG_ROTATE[0],
            when = LOG_ROTATE[1]
        )
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        _log.addHandler(handler)

        # Initiate the connection
        host, port = server['host'], server['port']
        overssl = security.getboolean('overssl')

        _log.info('Connect to %s:%s [SSL=%s].', host, port, overssl)

        if overssl:
            eubin = EubinSSL(host, port)
        else:
            eubin = Eubin(host, port)

        # Authorization
        user = account['user']
        password = get_password(account['pass'], account['passtype'])
        apop = security.getboolean('apop')

        _log.info("Login as '%s' [APOP=%s]", user, apop)
        eubin.login(user, password, apop=apop)

        # Do some transaction
        dest = os.path.expanduser(retrieval['dest'])
        leavecopy = retrieval.getboolean('leavecopy')

        _log.info('Start fetching mails to %s [leavecopy=%s]', dest, leavecopy)
        stat = eubin.fetchmail(dest, leavecopy=leavecopy)

        # Enter the update state.
        _log.info("Delivered: %s mails (%s bytes)", *stat)
        eubin.quit()

        # Detach logging handler
        _log.removeHandler(handler)

if __name__ == '__main__':
    main()
