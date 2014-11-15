__author__ = 'marcel'

from LCDController import *

lcd = LCD(4, 20)

lcd.set_line("time", TimeLine(lcd, 1, lcd.columns))
lcd.set_line("station", MPDLine(lcd, 2, lcd.columns, "name", align='c'))
lcd.set_line("song", MPDLine(lcd, 3, lcd.columns, "title"))

lcd.lineContainer["time"].run_every()
lcd.lineContainer["station"].run_every()
lcd.lineContainer["song"].run_every()
