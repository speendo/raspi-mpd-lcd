__author__ = 'marcel'

from i2clibraries import i2c_lcd as i2c_lcd_prev


class i2c_lcd(i2c_lcd_prev.i2c_lcd):

	def writeChar(self, char):
		if (char == 'ä') | (char == 'Ä'):
			super().writeChar(chr(225))
		elif char == 'ß':
			super().writeChar(chr(226))
		elif (char == 'ö') | (char == 'Ö'):
			super().writeChar(chr(239))
		elif (char == 'ü') | (char == 'Ü'):
			super().writeChar(chr(245))
		else:
			super().writeChar(char)
