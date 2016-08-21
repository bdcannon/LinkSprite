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

    pic_dim_cmd = b'\x56\x00\x31\x05\x04\x01\x00\x19' # still needs additional byte
    pic_dim_resp = b'\x76\x00\x31\x00\x00'

    # Read the buffer content
    # read_cont + address(H L) + read_cont_sep + read_size + read_cont_delay
    read_cont = b'\x56\x00\x32\x0C\x00\x0A\x00\x00'
    read_cont_sep = b'\x00\x00'
    read_size = b'\x0F\x00'
    read_size_inc = int.from_bytes(read_size, byteorder='big')
    read_cont_delay = b'\x00\x0A'
    read_resp = b'\x76\x00\x32\x00\x00'
    read_start = b'\xFF\xD8'
    read_end = b'\xFF\xD9'

    # done (stop taking pictures?)
    done_cmd = b'\x56\x00\x36\x01\x03'
    done_resp = b'\x76\x00\x36\x00\x00'

    # Baud command
    baud_cmd = b'\x56\x00\x24\x03\x01'
    baud_resp = b'\x76\x00\x24\x00\x00'

    # Picture Sizes
    pic_sizes = {'320x240' : b'\x11',
                 '640x480' : b'\x00',
                 '160x120' : b'\x22',}

    baud_rates = { 9600 : b'\xAE\xC8',
                   19200 : b'\x56\xE4',
                   38400 : b'\x2A\xF2',
                   57600 : b'\x1C\x4C',
                   115200 : b'\x0D\xA6',}

    default_baud = 38400

    def __init__(self, serial):
        self.serial = serial
        self.clearPort()
        # If miss on lookup for picture size, return default
        self.pic_sizes.setdefault('320x240')

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
        Tries to reset the camera. Need to clean this up
        """
        success = False
        resp = b''

        self.clearPort()

        # Will hang here if there's a problem
        while not b'Init end\r\n' in resp :
            self.serial.write(self.rst_cmd)
            time.sleep(.1)
            resp = self.serial.read(len(self.rst_resp))
            self.serial.baudrate = self.default_baud

        if b'Init end\r\n' in resp :
            success = True
        else :
            print(resp)

        time.sleep(2)

        return success

    # Reads and returns the processed serial data so its only jpg data
    def readChunk(self, address) :
        chunk = None

        cmd = self.read_cont + address + self.read_cont_sep + self.read_size + self.read_cont_delay
        self.serial.write(cmd)

        resp = self.serial.read(self.read_size_inc + (len(self.read_resp) * 2))

        if resp.endswith(self.read_resp) :
          chunk = resp[5:-5] # Remove the first and last 7 bytes

        return chunk

    def readPicture(self, file) :
        address = 0
        resp = bytearray()

        while not resp.strip().endswith(self.read_end) :
            print('At address %d' % address)
            addressBytes = address.to_bytes(2, byteorder='big')
            chunk = self.readChunk(addressBytes)
            resp.extend(chunk)
            address += self.read_size_inc

            # Check if we were at the end
            if self.read_end in chunk :
              break

        end_index = bytes(resp).index(self.read_end)

        with open(file, 'w+b') as f :
            resp = resp[:end_index + 2]
            print('Bytes in picture : %d' % len(resp))
            f.write(resp)
            f.close()

    def getPicDimBytes(self, size):
         size_bytes = self.pic_sizes.get(size)

         # Missing Key, we don't have that size
         if size_bytes is None :
             print('Warning! Camera does not support %s' % size)
             print ('Using default 320x240')
             size_bytes = self.pic_sizes.get('320x240')

         return size_bytes

    def setPicDim(self, size):
        size_byte = self.getPicDimBytes(size)
        dim_cmd = self.pic_dim_cmd + size_byte

        self.serial.write(dim_cmd)
        resp = self.serial.read(len(self.pic_dim_resp))
        return resp == self.pic_dim_resp

    def setCompression(self, compression) :
        """ Sets the compression ration for the jpg image. Expecting values of
        0 - 255
        """
        if compression > 255 :
            compression = 255

        comp_bytes = compression.to_bytes(1, byteorder='big')
        # print(list(self.comp_cmd + comp_bytes))
        self.serial.write(self.comp_cmd + comp_bytes)
        resp = self.serial.read(len(self.comp_resp))
        time.sleep(.25)

        return resp == self.comp_resp

    # Try to clear anything thats in the serialPort buffer
    def clearPort(self):
        """Tries to empty the buffer for the camera. Just in case there's any garbage
        """
        while self.serial.in_waiting :
            self.serial.read(self.serial.in_waiting)

        return self.serial.in_waiting

    def getWaiting(self):
        """Returns how many bytes are waiting to be read in the serial buffer.
        """
        return self.serial.in_waiting

    def getPicSize(self) :
        """ Return the size of the picture that is sitting in the buffer of the
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

    def getBaudBytes(self, baud):
        """ Returns the last two bytes for the baud command
        """
        baud_bytes = self.baud_rates.get(baud)
        if baud_bytes is None :
            baud_bytes = self.baud_rates.get(38400)

        return baud_bytes

    def changeBaud(self, baud) :
        """ Attempts to change the baud rate of the camera. I don't know when to
        switch..
        """
        success = False
        baud_bytes = self.getBaudBytes(baud)
        baud_cmd = self.baud_cmd + baud_bytes

        self.serial.write(baud_cmd)  # Try to change the cameras baud
        time.sleep(.1)
        resp = self.serial.read(self.serial.in_waiting)

        if len(resp) >= len(self.baud_resp) :
            print('Updated the baud')
            self.serial.baudrate = baud # update the baudrate
            success = True
        else :
            print(resp)
        return success


    def done(self) :
        """ Tells the Camera to stop taking pictures?
        """
        self.serial.write(self.done_cmd)
        resp = self.serial.read(len(self.done_resp))
        return resp == self.done_resp
