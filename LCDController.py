# -*- coding: utf-8 -*-
__author__ = 'marcel'

import LCDDriver
import threading


class LCD:
	def __init__(self, lines, columns, locale = None):
		# init lcd
		self.lcd = LCDDriver.LCD(locale = locale)

		# Lock
		self.lock = threading.RLock()

		# how many lines and columns
		self.lines = lines
		self.columns = columns
		# array containing the lines
		self.line_container = dict()

		# position
		self.cursor = (0, 0)

		# state
		self.suspend = False

	def backlight(self, stat):
		self.lock.acquire()
		try:
			self.lcd.backlight(stat)
		finally:
			self.lock.release()

	def set_line(self, name, lcd_line):
		if (lcd_line.line_number <= 0) | (lcd_line.line_number > self.lines):
			raise ValueError("Not a valid line number!")
		else:
			# check if line is reserved
			for cur_line in self.line_container.values():
				if cur_line.line_number == lcd_line.line_number:
					raise ValueError("Line already in use!")

			# else go ahead
			self.line_container[name] = lcd_line

		return lcd_line

	def remove_line(self, line):
		self.line_container[line].set_text(self.columns * " ")

		del self.line_container[line]

	def set_position(self, line, column):
		self.lock.acquire()
		try:
			self.lcd.set_position(line, column)

			# update current position
			self.cursor = (line, column)

		finally:
			self.lock.release()

	def write_char_at(self, line, column, char):
			self.lock.acquire()
			try:
				if (self.cursor[0] != line) | (self.cursor[1] != column):
					self.set_position(line, column)
				self.lcd.write(char)
				self.cursor = (line, column + 1)
			finally:
				self.lock.release()

	def standby(self):
		if not self.suspend:
			self.suspend = True

			for line in self.line_container.values():
				line.lock.acquire()

			self.lcd.clear_display()
			self.backlight(False)

	def resume(self):
		if self.suspend:
			self.suspend = False

			for line in self.line_container.values():
				line.lock.release()
				line.resume()

			self.backlight(True)
