#!/usr/bin/env python3

__author__ = 'marcel'

from lib.LCDController import *
from lib.LineController import *

lcd = LCD(4, 20)

lcd.set_line("time", TimeLine(lcd, 1))
lcd.set_line("station", MPDLine(lcd, 2, "name", align='c'))
lcd.set_line("song", MPDLine(lcd, 3, "title"))
lcd.set_line("proverb", FetchLine(lcd, 4, "http://sprichwortgenerator.de/plugin.php"))

lcd.lineContainer["time"].run_every()
lcd.lineContainer["station"].run_every()
lcd.lineContainer["song"].run_every()
lcd.lineContainer["proverb"].run_every()

import time
time.sleep(3)
print("Suspend")
lcd.standby()
time.sleep(2)
print("Resume")
lcd.resume()

