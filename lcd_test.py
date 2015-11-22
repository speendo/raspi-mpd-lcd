# -*- coding: utf-8 -*-
import lcd_driver

import locale_de

locale = locale_de.LocaleDE()

lcd = lcd_driver.LCD(locale = locale)

while True:
	line = int(input("Line: "))
	column = int(input("Column: "))
	lcd.set_position(line, column)
	
	text = input("Text: ")
	lcd.write(text)

