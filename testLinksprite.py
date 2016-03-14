import unittest
import serial
from LinkSprite import LinkSprite
import time
import os.path

current_baud = 38400

serial = serial.Serial('/dev/ttyUSB1', current_baud, timeout=1)
# serial = serial.Serial('/dev/tty.usbserial-A5027XNU', 38400, timeout=1)

class TestLinkSprite(unittest.TestCase):
    def setUp(self):
        self.ls = LinkSprite(serial)
        self.ls.clearPort()
        self.ls.reset()
        time.sleep(.1)

    def tearDown(self) :
        self.ls.reset()
        self.ls.serial.baudrate = current_baud

    def getImageDimensions(self, f):
        """ A utility method to make sure the dimensions of the jpg file were
        set over serial correctly
        """
        sof0 = b'\xFF\xC0'  # Marker for meta info about the jpg
        height_offset = 5 # two byte width
        width_offset = 7  # two byte width

        pic_height = None
        pic_width = None

        with open(f, 'r+b') as pic_file :
            pic_data = pic_file.read()
            index = pic_data.index(sof0)

            height_index = index + height_offset
            width_index = index + width_offset

            pic_height = int.from_bytes(pic_data[height_index : height_index + 2], byteorder='big')
            pic_width = int.from_bytes(pic_data[width_index : width_index + 2], byteorder='big')

            pic_file.close()

        print(str(pic_width) + 'x' + str(pic_height))
        return (pic_width, pic_height)



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


    def testSetImageSize(self):
        """ Test setting the image size over serial. Subsequent pictures Should
        have their dimensions change accordingly
        """
        res = self.ls.setPicDim('160x120')
        self.ls.reset()
        self.ls.takePic()
        self.ls.readPicture('160x120.jpg')
        dim = self.getImageDimensions('160x120.jpg')
        self.assertEqual(dim[0], 160)
        self.assertEqual(dim[1], 120)
        self.assertTrue(res)

        res = self.ls.setPicDim('320x240')
        self.ls.reset()
        self.ls.takePic()
        self.ls.readPicture('320x240.jpg')
        dim = self.getImageDimensions('320x240.jpg')
        self.assertEqual(dim[0], 320)
        self.assertEqual(dim[1], 240)
        self.assertTrue(res)

        res = self.ls.setPicDim('640x480')
        self.ls.reset()
        self.ls.takePic()
        self.ls.readPicture('640x480.jpg')
        dim = self.getImageDimensions('640x480.jpg')
        self.assertEqual(dim[0], 640)
        self.assertEqual(dim[1], 480)
        self.assertTrue(res)

        res = self.ls.setPicDim('12x12')
        self.ls.reset()
        self.ls.takePic()
        self.ls.readPicture('12x12.jpg')
        dim = self.getImageDimensions('12x12.jpg')
        self.assertEqual(dim[0], 320)
        self.assertEqual(dim[1], 240)
        self.assertTrue(res)

    def testReadPic(self):
        self.ls.takePic()
        self.ls.readPicture('pic.jpg')
        self.assertTrue(os.path.isfile('pic.jpg'))

    def testTakePicture(self):
        resp = self.ls.takePic()

        self.assertTrue(resp[0] > 0) # Make sure we got some more bytes
        self.assertIsInstance(resp[1], bytes)
        self.assertEqual(resp[0], len(resp[1]))

    def testPictureDimBytes(self) :
        size_byte = self.ls.getPicDimBytes('320x240')
        self.assertEqual(size_byte, b'\x11')

        size_byte = self.ls.getPicDimBytes('640x480')
        self.assertEqual(size_byte, b'\x00')

        size_byte = self.ls.getPicDimBytes('160x120')
        self.assertEqual(size_byte, b'\x22')

        size_byte = self.ls.getPicDimBytes('132x12') # Should miss and get default
        self.assertEqual(size_byte, b'\x11')

    def testFlow(self):
        """
            Tests the work flow that's supposed to happen....
        """
        for n in range(0, 10) :
            comp_res = self.ls.setCompression(50)
            time.sleep(.1)
            self.assertTrue(comp_res)
            self.ls.takePic()
            self.ls.readPicture('flow.jpg')
            self.ls.done()

    def testCompressionRatio(self):
         for n in range(0, 260, 15) :
             # Set the compression and slleeeeepppppp
             self.ls.setCompression(n)
             time.sleep(.1)

             self.ls.takePic()
             self.ls.readPicture('./compression_test/comp' + str(n) + '.jpg')
             self.assertTrue(self.ls.done())
             time.sleep(.1)

    def testBaudBytes(self) :
        baud_bytes = self.ls.getBaudBytes(38400)
        self.assertEqual(baud_bytes, b'\x2A\xF2')

        baud_bytes = self.ls.getBaudBytes(115200)
        self.assertEqual(baud_bytes, b'\x0D\xA6')

    def testChangeBaudRate(self) :
        next_baud = 115200

        # Make sure current baud is good
        resp = self.ls.reset()
        self.assertTrue(resp)

        # Try changing the baud
        resp = self.ls.changeBaud(next_baud)
        self.assertTrue(resp)

        # If we get this far try other things
        self.ls.setCompression(10)
        time.sleep(.1)
        self.ls.takePic()
        self.ls.readPicture('fastBaud.jpg')
        self.assertTrue(self.ls.done())

if __name__ == '__main__':
  unittest.main()
