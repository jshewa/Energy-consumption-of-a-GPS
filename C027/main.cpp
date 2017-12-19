#include "GPS.h"
#ifdef TARGET_UBLOX_C027
 #include "ublox_low_level_api.h"
#endif





int main (void){
    ublox_gps_powerOn();
    GPSSerial gps(GPSTXD,GPSRXD);
    int baud = GPSBAUD;
    Serial pc(USBTX, USBRX);
    pc.baud(baud);
    
    
    while (1)
    {
        // transfer data from pc to gps
        if (pc.readable() && gps.writeable())
            gps.putc(pc.getc());
        // transfer data from gps to pc
        if (gps.readable() && pc.writeable())
            pc.putc(gps.getc());
    }
    
    
    
    
    return 0;
    }