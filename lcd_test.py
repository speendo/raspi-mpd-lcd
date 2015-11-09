# -*- coding: utf-8 -*-
import LCDDriver

import LocaleDE

locale = LocaleDE.LocaleDE()

lcd = LCDDriver.LCD(locale = locale)

while True:
	line = int(input("Line: "))
	column = int(input("Column: "))
	lcd.set_position(line, column)
	
	text = input("Text: ")
	for c in text:
		lcd.write(c)

