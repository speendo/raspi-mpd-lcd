__author__ = 'marcel'

from i2clibraries import i2c_lcd as i2c_lcd_prev


class i2c_lcd_new(i2c_lcd_prev):
#	def __init__(self, addr, port, en, rw, rs, d4, d5, d6, d7, backlight = -1):
#		super().__init__(self, addr, port, en, rw, rs, d4, d5, d6, d7, backlight=backlight)

	def writeChar(self, char):
		if char == 'ä' | char == 'Ä':
			super().writeChar(chr(225))
		elif char == 'ß':
			super().writeChar(chr(226))
		elif char == 'ö' | char == 'Ö':
			super().writeChar(chr(239))
		elif char == 'ü' | char == 'Ü':
			super().writeChar(chr(245))
		else:
			super().writeChar(char)
