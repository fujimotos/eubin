import unittest
from eubin import maildir

class TestMaildir(unittest.TestCase):
    def test_getuid(self):
        uid1, uid2 = (maildir._getuid() for x in range(2))
        self.assertNotEqual(uid1, uid2)

if __name__ == '__main__':
    unittest.main()
