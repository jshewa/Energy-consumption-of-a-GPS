from machine import Timer
import time
import gc
import binascii

class L76GNSS:
    STANDBY = bytes( [0x24,0x50,0x4D,0x54,0x4B,0x31,0x36,0x31,0x2C,0x30,0x2A,0x32,0x38,0xD,0xA])
    GLONASS = bytes( [0x24,0x50,0x4D,0x54,0x4B,0x33,0x35,0x33,0x2C,0x30,0x2C,0x31,0x2A,0x33,0x36,0xD,0xA]) 
    COLD_START = bytes( [0x24,0x50,0x4D,0x54,0x4B,0x31,0x30,0x34,0x2A,0x33,0x37,0xD,0xA])
    PERIODIC_MODE = bytes( [0x24,0x50,0x4D,0x54,0x4B,0x32,0x32,0x35,0x2C,0x32,0x2C,0x33,0x30,0x30,0x30,0x2C,0x31,0x32,0x30,0x30,0x30,0x2C,0x31,0x38,0x30,0x30,0x30,0x2C,0x37,0x32,0x30,0x30,0x30,0x2A,0x31,0x35])

    GPS_I2CADDR = const(0x10)

    def __init__(self, pytrack=None, sda='P22', scl='P21', timeout=None):
        if pytrack is not None:
            self.i2c = pytrack.i2c
        else:
            from machine import I2C
            self.i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))

        self.chrono = Timer.Chrono()

        self.timeout = timeout
        self.timeout_status = True

        self.reg = bytearray(1)
        self.i2c.writeto(GPS_I2CADDR, self.reg)
        self.fix = 0
        self.first_fix=0
        self.timestamp= 0

        self.lat_d = 0
        self.lon_d = 0

    def write_gps(self,data,wait=True):
        print(data)
        self.i2c.writeto(GPS_I2CADDR, data)
        if wait:
             self.wait_gps()    
    def wait_gps(self):
        count = 0
        time.sleep_us(10)
        while self.i2c.readfrom(GPS_I2CADDR, 1)[0] != 0xFF:
            time.sleep_us(100)
            count += 1
            if (count > 500):  # timeout after 50ms
                raise Exception('Pytrack board timeout')


           
    def _read(self):
        self.reg = self.i2c.readfrom(GPS_I2CADDR, 64)
        return self.reg
    def _set_time(self,gpgga_s):
        print('_set_time')
        self.timestamp = gpgga_s[1]
        print('timestamp set',self.timestamp)
    def _convert_coords(self, gpgga_s):
        lat = gpgga_s[1]
        lat_d = (float(lat) // 100) + ((float(lat) % 100) / 60)
        lon = gpgga_s[3]
        lon_d = (float(lon) // 100) + ((float(lon) % 100) / 60)
        if gpgga_s[2] == 'S':
            lat_d *= -1
        if gpgga_s[4] == 'W':
            lon_d *= -1
        return(lat_d, lon_d)
    def get_fix(self,gpgga_s):
        temp_fix= gpgga_s[6]
        self.fix = int(temp_fix)

    def coordinates(self, debug=False):
        lat_d, lon_d, debug_timeout = None, None, False
        if self.timeout != None:
            self.chrono.reset()
            self.chrono.start()
        nmea = b''
        while True:
            if self.timeout != None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if self.timeout_status != True:
                gc.collect()
                break
            nmea += self._read().lstrip(b'\n\n').rstrip(b'\n\n')
            gpgga_idx = nmea.find(b'GPGGA')
            if gpgga_idx >= 0:
                gpgga = nmea[gpgga_idx:]
                e_idx = gpgga.find(b'\r\n')
                if e_idx >= 0:
                    try:
                        gpgga = gpgga[:e_idx].decode('ascii')
                        gpgga_s = gpgga.split(',')
                        print(gpgga_s)
                        self.get_fix(gpgga_s)
                        if(self.fix >0):
                            if(self.first_fix == 0):
                                self.first_fix = 1
                                self._set_time(gpgga_s)
                            #self._get_clock(gpgga_s)
                            self.lat_d, self.lon_d = self._convert_coords(gpgga_s)
                    except Exception:
                        pass
                    finally:
                        nmea = nmea[(gpgga_idx + e_idx):]
                        gc.collect()
                        break
            else:
                gc.collect()
                if len(nmea) > 4096:
                    nmea = b''
           # time.sleep(0.1)
        self.timeout_status = True
        if debug and debug_timeout:
            print('GPS timed out after %f seconds' % (chrono_timeout))
            return(None, None)
        else:
            return(lat_d, lon_d)


