"""
  This class
"""
import time

class LinkSprite :
    rst_cmd = b'\x56\x00\x26\x00'
    rst_resp = b'v\x00&\x00\x00VC0703 1.00\r\nCtrl infr exist\r\nUser-defined sensor\r\n625\r\nInit end\r\n'

    pic_cmd = b'\x56\x00\x36\x01\x00'
    pic_resp = b'\x76\x00\x36\x00\x00'

    pic_size_cmd = b'\x56\x00\x34\x01\x00'
    pic_size_resp = b'\x76\x00\x34\x00\x04\x00\x00\xFF\xFF'

    # Command for compression ratio
    comp_cmd = b'\x56\x00\x31\x05\x01\x01\x12\x04'
    comp_resp = b'\x76\x00\x31\x00\x00'


    def __init__(self, serial):
        self.serial = serial
        self.clearPort()

    def waitForInit(self) :
        self.serial.write(self.pic_cmd)
        resp = self.serial.read(67)

        while not resp.strip().endswith(b'Init end') :
            time.sleep(3)
            self.serial.read(self.serial.in_waiting)
            self.serial.write(self.pic_cmd)
            resp = self.serial.read(67)

    def reset(self) :
        """
        Tries to reset the camera
        """
        self.serial.write(self.rst_cmd)
        resp_data = self.serial.read(len(self.rst_resp))

        if resp_data == self.rst_resp :
            print('Camera Reset')

        return (len(resp_data), resp_data)

    def setCompression(self, compression) :
        """
        Sets the compression ration for the jpg image. Expecting values of
        0 - 255
        """
        if compression > 255 :
            compression = 255

        comp_bytes = compression.to_bytes(1, byteorder='big')
        print(list(self.comp_cmd + comp_bytes))
        self.serial.write(self.comp_cmd + comp_bytes)

        resp = self.serial.read(len(self.comp_resp) + 2)
        print('Compression resp')
        print(list(resp))
        resp_comp = int.from_bytes(resp[-1:], byteorder='big')
        print(resp_comp)

        return(resp_comp, resp)


    # Try to clear anything thats in the serialPort buffer
    def clearPort(self):
        """
        Tries to empty the buffer for the camera. Just in case there's any garbage
        """
        while self.serial.in_waiting :
            self.serial.read(self.serial.in_waiting)
        print('Bytes in waiting %d' % self.serial.in_waiting)

    def getWaiting(self):
        """
        Returns how many bytes are waiting to be read in the serial buffer.
        """
        return self.serial.in_waiting

    def getPicSize(self) :
        """
        Return the size of the picture that is sitting in the buffer of the
        camera. Read this many bytes later
        """
        self.serial.write(self.pic_size_cmd)
        resp = self.serial.read(len(self.pic_size_resp))
        size = int.from_bytes(resp[-2:], byteorder='big')
        return (size, resp)

    def takePic(self):
        self.serial.write(self.pic_cmd)
        resp = self.serial.read(len(self.pic_resp))
        if resp == self.pic_resp :   # Successful
            print('Snap!')
        return(len(resp), resp)
