import unittest
from linksprite import getPicSize

class TestLinkSprite(unittest.TestCase) :
  def testPicSize(self):
    size_resp = b'\x76\x00\x34\x00\x00\xFF\xFF'
    size = getPicSize(size_resp)
    self.assertEqual(size, 65535)

    size_resp = b'\x76\x00\x34\x00\x00\xAA\xFF'
    size = getPicSize(size_resp)
    self.assertEqual(size, 43775)

if __name__ == '__main__':
  unittest.main()
