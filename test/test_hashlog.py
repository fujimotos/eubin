import unittest
import os
from tempfile import TemporaryDirectory
from eubin import hashlog

MD5SUM = {
    'a': '0cc175b9c0f1b6a831c399e269772661',
    'b': '92eb5ffee6ae2fec3ad71c777531578f',
    'c': '4a8a08f09d37b73795649038408b5f33',
    'd': '8277e0910d750195b448797616e091ad',
    'ab': '187ef4436122d1cc2f40dc2b92f0eba0'
}

class TestHashlog(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.logpath = os.path.join(self.tmpdir.name, 'hashlog')

        with open(self.logpath, 'w') as fw:
            fw.write(MD5SUM['a'] + '\n')
            fw.write(MD5SUM['b'] + '\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load(self):
        hashset = hashlog.load(self.logpath)
        self.assertEqual(hashset, {MD5SUM['a'], MD5SUM['b']})

    def test_append(self):
        hashlog.append(self.logpath, MD5SUM['c'])
        hashlog.append(self.logpath, MD5SUM['d'])
        with open(self.logpath) as fp:
            self.assertEqual(fp.readline(), MD5SUM['a'] + '\n')
            self.assertEqual(fp.readline(), MD5SUM['b'] + '\n')
            self.assertEqual(fp.readline(), MD5SUM['c'] + '\n')
            self.assertEqual(fp.readline(), MD5SUM['d'] + '\n')

    def test_create(self):
        hashlog.create(self.logpath, (MD5SUM['c'], MD5SUM['d']))
        with open(self.logpath) as fp:
            self.assertEqual(fp.readline(), MD5SUM['c'] + '\n')
            self.assertEqual(fp.readline(), MD5SUM['d'] + '\n')

    def test_md5sum(self):
        for key in MD5SUM:
            md5sum = hashlog.md5sum([key.encode()])
            self.assertEqual(md5sum, MD5SUM[key])

        # hashing several lines
        md5sum = hashlog.md5sum([b'a', b'b'])
        self.assertEqual(md5sum, MD5SUM['ab'])

if __name__ == '__main__':
    unittest.main()
