import machine
import math
import network
import os
import time
import utime
from machine import RTC
from machine import SD
from machine import Timer
from L76GNSS import L76GNSS
from pytrack import Pytrack
from machine import Pin
from network import WLAN
from network import Bluetooth
# setup as a station
#"address": "192.168.4.1"
import gc





rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')


# initialize ``P9`` in gpio mode and make it an output
p_out = Pin('P20', mode=Pin.OUT)
p_out.value(0)

wlan= WLAN()
wlan.deinit()
bt = Bluetooth()
bt.deinit()


py = Pytrack()
#l76 = L76GNSS(py, timeout=2)
l76 = L76GNSS(py)
l76.write_gps(l76.COLD_START,False)
time.sleep(2)

p_out.value(1)
time.sleep(0.25)
p_out.value(0)
while (True):
    coord = l76.coordinates()
    print ("FIX:jared ", l76.fix)
    if (l76.first_fix ==1):
        print('timestamp: ',l76.timestamp)
        p_out.value(1)
        time.sleep(0.25)
        p_out.value(0)
        while(True):
            coord = l76.coordinates()
            print ("FIX: ", l76.fix)
            time.sleep(0.25)
