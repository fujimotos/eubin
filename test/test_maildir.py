import unittest
from eubin import maildir

class TestMaildir(unittest.TestCase):
    def test_getuid(self):
        self.assertNotEqual(maildir.getuid(), maildir.getuid())

if __name__ == '__main__':
    unittest.main()
