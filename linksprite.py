import serial
import time

reset = b'\x56\x00\x26\x00'
reset_resp = b'\x76\x00\x26\x00'

pic = b'\x56\x00\x36\x01\x00'
pic_resp = b'\x76\x00\x36\x00\x00'

# Picture response and size
jpg_size = b'\x56\x00\x34\x01\x00'
jpg_size_resp = b'\x76\x00\x34\x00\x04\x00\x00\xFF\xFF'

# Read the buffer content
# read_cont + address(H L) + read_cont_sep + read_size + read_cont_delay
read_cont = b'\x56\x00\x32\x0C\x00\x0A\x00\x00'
read_cont_sep = b'\x00\x00'
read_size = b'\x0C\x80'
read_size_inc = int.from_bytes(read_size, byteorder='big')
read_cont_delay = b'\x00\x0A'
read_resp = b'\x76\x00\x32\x00\x00'
read_start = b'\xFF\xD8'
read_end = b'\xFF\xD9'

jpg_end = b'\xFF\xD9'

def getPicSize(serial) :
    serial.write(jpg_size)
    resp = serial.read(len(jpg_size_resp))
    size = int.from_bytes(resp[-2:], byteorder='big')

    print('JPG size : %d' % size)

    return size

# Reads and returns the processed serial data so its only jpg data
def readChunk(address) :
    chunk = None

    cmd = read_cont + address + read_cont_sep + read_size + read_cont_delay
    serial.write(cmd)

    resp = serial.read(read_size_inc + (len(read_resp) * 2))

    if resp.endswith(read_resp) :
      chunk = resp[5:-5] # Remove the first and last 7 bytes

    return chunk

def readPicture(serial) :
    address = 0
    resp = b''

    while not resp.strip().endswith(jpg_end) :
        print('At address %d' % address)
        addressBytes = address.to_bytes(2, byteorder='big')
        chunk = readChunk(addressBytes)
        resp += chunk
        address += read_size_inc

        # Check if we were at the end
        if read_end in chunk :
          break

    end_index = resp.index(read_end)

    with open('pic.jpg', 'w+b') as f :
        resp = resp[:end_index + 2]
        print('Bytes in picture : %d' % len(resp))
        f.write(resp)
        f.close()


def resetCam(serial) :
    success = False

    serial.write(reset)
    resp = serial.read(len(reset_resp))

    print("Reset the camera") if resp == reset_resp else print("Camera Didn't Reset")
    if resp == reset_resp :
        success = True
    else :
        print(resp)

    return success

def waitForInit(serial) :
    serial.write(pic)
    resp = serial.read(67)

    while not resp.strip().endswith(b'Init end') :
        time.sleep(3)
        serial.read(serial.in_waiting)
        serial.write(pic)
        serial.read(67)

def clearBuffer(serial) :
    while serial.in_waiting :
      print('Clearing Bytes')
      serial.read(serial.in_waiting)

def takePic(serial) :
    success = False

    print('Taking a picture')
    serial.write(pic)
    resp = serial.read(len(pic_resp))
    # print (resp)

    print('Snap!') if resp == pic_resp else print('No Snap')


if __name__ == '__main__' :
    # with serial.Serial('/dev/tty.usbserial-A5027XNU', baudrate = 38400, timeout=1) as serial :
   with serial.Serial('/dev/ttyUSB0', 38400) as serial :

        if serial.isOpen() :
            print('It Worked')

            resetCam(serial)
            waitForInit(serial)
            clearBuffer(serial)
            takePic(serial)
            getPicSize(serial)
            readPicture(serial)


        serial.close()
