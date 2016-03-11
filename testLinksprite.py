import unittest
import serial
from LinkSprite import LinkSprite
import time

serial = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)

class TestLinkSprite(unittest.TestCase):
    def setUp(self):
        self.ls = LinkSprite(serial)
        self.ls.clearPort()
        self.ls.reset()
        time.sleep(1)

    def testClassInitiation(self):
        self.assertFalse(self.ls is None)

    def testReset(self) :
        # Returns
        rst_resp = (b'v\x00&\x00\x00VC0703 1.00\r\nCtrl infr exist\r\nUser-defined sensor\r\n625\r\nInit end\r\n')

        resp = self.ls.reset()
        self.assertTrue(resp[0] > 0) # Response length is greater than 0 bytes
        self.assertEqual(resp[1], rst_resp)
        self.assertEqual(self.ls.getWaiting(), 0)   # Check how many bytes are available

    def testGetPicSize(self) :
        self.ls.takePic()
        resp =  self.ls.getPicSize()

        self.assertIsInstance(resp[0], int)
        self.assertTrue(resp[0] > 0 and resp[0] <= 65535)

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
        self.assertIsInstance(resp[1], bytes)
        self.assertEqual(resp[0], len(resp[1]))

    def testCompressionRatio(self):
        resp = self.ls.setCompression(54)

        print(resp[0])
        print(resp[1])

        self.assertTrue(resp[0] > 0)
        self.assertTrue(resp[0] == 54)

        resp = self.ls.setCompression(255)
        self.assertTrue(resp[0] > 0)
        self.assertTrue(resp[0] == 255)

if __name__ == '__main__':
  unittest.main()
