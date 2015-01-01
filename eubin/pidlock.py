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
        if self.check():
            raise PIDLockException('process already running')

        with open(self.lockfile, 'w') as fw:
            fw.write(str(self.pid))

        return self

    def release(self):
        os.remove(self.lockfile)

    def check(self):
        # Check if the lock file does exist.
        if not os.path.exists(self.lockfile):
            return False

        # If the lock file does exist, then check the
        # corresponding process is still running.
        with open(self.lockfile) as fp:
            pid = int(fp.read())

        isalive = self._isalive(pid)

        if not isalive:
            _log.warning('Lock file found, but no process running as pid %s', pid)
            _log.warning('Clean up the old lock file')
            self.release()

        return isalive

    @staticmethod
    def _isalive(pid):
        if pid < 1: return False

        res = True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            res = False
        except:
            pass
        return res
