# LinkSprite
A simple Python class for the LinkSprite serial jpeg camera

This class covers most of the functionality of the LinkSprite camera from sparkfun. https://www.sparkfun.com/products/11610.
See the testLinkSprite file to get an idea of some usage. You can test your setup with the testLinkSprite file. I used
Adafruit's very nice [FTDI friend](https://www.adafruit.com/products/284) and an inexpensive usb to serial device 
[CP2102 breakout](http://goo.gl/tPL5mW) . Both seemed to work well.

Here's an simple example for increasing the baudrate, taking a picture, and saving it to file.

```python
import serial
from LinkSprite import LinkSprite

serial = serial.Serial('/dev/ttyUSB0', 38400, timeout=5)
ls = LinkSprite(serial)
ls.reset()
ls.changeBaud(115200)
ls.takePic()  
ls.readPicture('pic.jpg') # Reads the buffer and saves to file
ls.done() # Tell the camera you're done
```

I have not tested this code for python 2.7, but works well with python3.2+


Stuff that needs to be worked on.
1. Code Needs to be more robust
2. Some class methods are returning useless stuff
3. Thers some magic numbers and sleeps floating around
