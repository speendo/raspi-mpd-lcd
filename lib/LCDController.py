__author__ = 'marcel'

from i2c_lcd_patched import i2c_lcd
import threading


class LCD:
	def __init__(self, lines, columns):
		# init lcd
		self.lcd = i2c_lcd(0x27, 1, 2, 1, 0, 4, 5, 6, 7, 3)

		# Lock
		self.lock = threading.RLock()

		# how many lines and columns
		self.lines = lines
		self.columns = columns
		# array containing the lines
		self.lineContainer = dict()

		# position
		self.cursor = (0, 0)

		# remove cursor
		self.lcd.command(self.lcd.CMD_Display_Control | self.lcd.OPT_Enable_Display)
		# turn backlingt on
		self.backlight(True)

	def backlight(self, stat):
		if stat:
			self.lock.acquire()
			try:
				self.lcd.backLightOn()
			finally:
				self.lock.release()
		else:
			self.lock.acquire()
			try:
				self.lcd.backLightOff()
			finally:
				self.lock.release()

	def set_line(self, name, lcd_line):
		if (lcd_line.line_number <= 0) | (lcd_line.line_number > self.lines):
			raise ValueError("Not a valid line number!")
		else:
			# check if line is reserved
			for cur_line in self.lineContainer.values():
				if cur_line.line_number == lcd_line.line_number:
					raise ValueError("Line already in use!")

			# else go ahead
			self.lineContainer[name] = lcd_line

		return lcd_line

	def remove_line(self, line):
		self.lineContainer[line].set_text(self.columns * " ")

		del self.lineContainer[line]

	def set_position(self, line, column):
		self.lock.acquire()
		try:
			self.lcd.setPosition(line, column)

			# update current position
			self.cursor = (line, column)

		finally:
			self.lock.release()

	def write_char_at(self, line, column, char):
			self.lock.acquire()
			try:
				if (self.cursor[0] != line) | (self.cursor[1] != column):
					self.set_position(line, column)
				self.lcd.writeChar(char)
				self.cursor = (line, column + 1)
			finally:
				self.lock.release()

	def standby(self):
		for line in self.lineContainer.values():
			line.lock.acquire()

		self.lcd.command(self.lcd.CMD_Clear_Display)
		self.backlight(False)

	def resume(self):
		# reset timers
		for line in self.lineContainer.values():
			line.lock.release()
			line.resume()

		self.backlight(True)
		self.suspend = False