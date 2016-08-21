import serial
from LinkSprite import LinkSprite
import time
import os.path

serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

ls = LinkSprite(serial)
ls.reset()
print('Trying to set image size')
ls.setPicDim('640x480')
# ls.setCompression(50)
ls.reset()
ls.changeBaud(115200)
count = 1
ls.setCompression(200)
while 1 : 
	ls.takePic()
	ls.readPicture('640x280{}.jpg'.format(count))
	ls.done()
	time.sleep(.1)
	print('this is picture {}'.format(count))
	#time.sleep(2)
	count += 1

