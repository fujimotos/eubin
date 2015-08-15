import os
import logging

_log = logging.getLogger(__name__)

class PIDLockException(Exception):
    pass

class PIDLock:
    def __init__(self, lockfile):
        self.pid = os.getpid()
        self.lockfile = lockfile

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def acquire(self):
        pid = self.check()

        if pid is not None:
            raise PIDLockException('eubin already running as pid {}'.format(pid))

        with open(self.lockfile, 'w') as fw:
            fw.write(str(self.pid))

        return self

    def release(self):
        os.remove(self.lockfile)

    def check(self):
        if not os.path.exists(self.lockfile):
            return

        res = None

        with open(self.lockfile) as fp:
            pid = int(fp.read())

        if self.isalive(pid):
            res = pid
        else:
            _log.warning('Lock file found, but no process running as pid %s.', pid)
            _log.warning('Clean up the old lock file...')
            self.release()

        return res

    @staticmethod
    def isalive(pid):
        if pid < 1: return False

        res = True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            res = False
        except:
            pass
        return res
