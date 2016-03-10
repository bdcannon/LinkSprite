import unittest
import serial
from LinkSprite import LinkSprite

class TestLinkSprite(unittest.TestCase):
    def setUp(self):
        self.ls = LinkSprite()

    def testClassInitiation(self):
        self.ls = LinkSprite()
        self.assertFalse(self.ls is None)

      # Need to check fields

    def testReset(self) :
        # Returns
        rst_resp = (b'v\x00&\x00\x00VC0703 1.00\r\nCtrl infr exist\r\nUser-defined sensor\r\n625\r\nInit end\r\n')

        resp = self.ls.reset()
        self.assertTrue(resp[0] > 0) # Response length is greater than 0 bytes
        self.assertEqual(resp[1], rst_resp)
        self.assertEqual(ls.getWaiting(), 0)   # Check how many bytes are available


    def testGetImageSize(self):
        sizeBase = b'\x56\x00\x31\x05\x04\x01\x00'
        sz_320x240 = sizeBase + b'\x19\x11'
        sz_640x480 = sizeBase + b'\x19\x00'
        sz_160x120 = sizeBase + b'\x19\x22'
        sz_resp = b'\x76\x00\x31\x00\x00'

        resp = self.ls.setSize('320x240')
        self.assertEqual(resp[1], sz_resp)

    def testTakePicture(self):
        resp = self.ls.takePic()

        self.assertTrue(resp[0] > 0) # Make sure we got some more bytes
        self.asserIsInstance(resp[1], bytes)
        self.assertEqual(resp[0], len(resp[1]))

    def testCompressionRatio(self):
        comp_resp = b'\x56\x00\x31\x05\x01\x01\x12\x04\x36'

        resp = self.ls.setCompression(54)

        self.assertTrue(resp[0] > 0)
        self.assertEqual(resp[1], comp_resp)

if __name__ == '__main__':
  unittest.main()
