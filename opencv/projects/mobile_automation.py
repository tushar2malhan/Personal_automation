import time
from ppadb.client import Client as AdbClient


client = AdbClient(host="127.0.0.1", port=5037) # Default is "127.0.0.1" and 5037
devices = client.devices()

if len(devices) == 0:
    print('No devices')
    quit()

device = devices[0]

print(f'Connected to {device}')

device.shell('input touchscreen tap 370 1150')
time.sleep(1)
device.shell('input touchscreen tap 1030 1103')
time.sleep(1)
device.shell('input touchscreen swipe 207 1684 476 1915')
time.sleep(1)
device.shell('input touchscreen swipe 476 1915 956 1902')
time.sleep(1)
device.shell('input touchscreen swipe 956 1902 1164 1556')

#Commands to control phone
#device.shell('input touchscreen tap x y')

#device.shell('input touchscreen swipe x1 y1 x2 y2')

#device.shell('Input keyevent eventID')

#device.shell('Input text "Enter your text here"')