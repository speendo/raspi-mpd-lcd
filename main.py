#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'marcel'

from lcd_controller import *
from line_controller import *

from locale_de import LocaleDE

locale_de = LocaleDE()

lcd = LCD(4, 20, locale = locale_de)

lcd.set_line("time", TimeLine(lcd, 1))
lcd.set_line("station", MPDLine(lcd, 2, "name", align='c'))
lcd.set_line("song", MPDLine(lcd, 3, "title"))
lcd.set_line("proverb", FetchLine(lcd, 4, "http://sprichwortgenerator.de/plugin.php"))

lcd.line_container["time"].run_every()
lcd.line_container["station"].run_every()
lcd.line_container["song"].run_every()
lcd.line_container["proverb"].run_every()

import time
time.sleep(3)
print("Suspend")
lcd.standby()
time.sleep(2)
print("Resume")
lcd.resume()

