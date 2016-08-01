import unittest
import os
from tempfile import TemporaryDirectory
from eubin import statelog

class TestHashlog(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.logpath = os.path.join(self.tmpdir.name, 'statelog')

        with open(self.logpath, 'wb') as fw:
            fw.write(b'001\n')
            fw.write(b'002\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load(self):
        state = statelog.load(self.logpath)
        self.assertEqual(state, {b'001', b'002'})

    def test_create(self):
        statelog.save(self.logpath, {b'001', b'002'})
        with open(self.logpath, 'rb') as fp:
            self.assertEqual(fp.readline(), b'001\n')
            self.assertEqual(fp.readline(), b'002\n')

if __name__ == '__main__':
    unittest.main()
