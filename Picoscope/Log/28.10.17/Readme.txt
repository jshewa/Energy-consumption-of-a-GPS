Goal:

1. Measure the power consumption when everything is disabled. This is the baseline

2. Measure the power consumption when the device is in deepsleep but the gps is on
	-3.4 mv

3. Measure the power consumption when the device is deepsleep and the gps is off
	-4.3 mv


When the device wakes up from deepsleep, it does not contiune to execute code from where it slept but executes the
boot.py and main.py files again. 

The GPS is not on when the device is set in deepsleep with V_bck powered on but its in backup mode. 
Back up mode requires lower power consumption than standby mode. In this mode, the module stops to
acquire and track satellites. UART1 is not accessible. But the backed-up memory in RTC domain which
contains all the necessary GPS information for quick start-up and a small amount of user configuration
variables is alive. Due to the backed-up memory, EASY technology is available. The current consumption
in this mode is about 7uA. 

Tried using forum suggestion and got a drop from 78 mv to 70 mv...
