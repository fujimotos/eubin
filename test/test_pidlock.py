import unittest
import os
from tempfile import TemporaryDirectory
from eubin.pidlock import PIDLock, PIDLockException

class TestPIDLock(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.lockfile = os.path.join(self.tmpdir.name, 'lockfile')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_acquire(self):
        lock = PIDLock(self.lockfile)
        lock.acquire()
        self.assertTrue(lock.check())

    def test_acquire_again(self):
        lock = PIDLock(self.lockfile)
        with lock.acquire():
            self.assertRaises(PIDLockException, lock.acquire)

    def test_cleanup_debris(self):
        with open(self.lockfile, 'w') as f:
            f.write('0')  # Non existent pid

        lock = PIDLock(self.lockfile)
        lock.acquire()
        self.assertTrue(lock.check())

    def test_release(self):
        lock = PIDLock(self.lockfile)
        lock.acquire()
        lock.release()
        self.assertFalse(lock.check())

    def test_acquire_withcontext(self):
        lock = PIDLock(self.lockfile)
        with lock.acquire():
            self.assertTrue(lock.check())
        self.assertFalse(lock.check())

if __name__ == '__main__':
    unittest.main()
