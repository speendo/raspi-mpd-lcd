__author__ = 'marcel'

from i2clibraries import i2c_lcd
import threading


class LCD:
	def __init__(self, lines, columns):
		# init lcd
		self.lcd = i2c_lcd.i2c_lcd(0x27, 1, 2, 1, 0, 4, 5, 6, 7, 3)

		# Lock
		self.lock = threading.RLock()

		# how many lines and columns
		self.lines = lines
		self.columns = columns
		# array containing the lines
		self.lineContainer = dict()

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
			raise ValueError("Not a valid line number")
		else:
			self.lineContainer[name] = lcd_line

	def set_position(self, line, column):
		self.lock.acquire()
		try:
			self.lcd.setPosition(line, column)
		finally:
			self.lock.release()

	def write_char_at(self, line, column, char):
		self.lock.acquire()
		try:
			self.set_position(line, column)
			self.lcd.writeChar(char)
		finally:
			self.lock.release()


class LCDLine(threading.Thread):
	import time
	import math

	def __init__(self, lcd, line_number, columns, refresh_interval=0.5, step_interval=2, start_duration=5,
	             end_duration=5):
		super().__init__()
		self.lcd = lcd
		self.line_number = line_number
		self.columns = columns
		self.refresh_interval = refresh_interval
		self.step_interval = step_interval
		self.start_duration = start_duration
		self.end_duration = end_duration
		# current text
		self.text = ""
		# current position
		self.text_pos = 0
		# marquee necessary?
		self.do_marquee = False
		# current text
		self._current_text_ = columns * " "
		# last marquee step
		self.last_marquee_step = None

	def run_every(self):
		self._write_string_()
		self._time_for_marquee_()
		threading.Timer(self.refresh_interval, self.run_every).start()

	def _reset_line_(self):
		self.lcd.set_position(self.line_number, 0)

	def format_text(self, text, align='l'):
		if len(text) < self.columns:
			if align == 'r':
				return (self.columns - len(text)) * " " + text
			elif align == 'c':
				return self.math.floor((self.columns - len(text)) / 2) * " " + \
				       text + self.math.ceil((self.columns - len(text)) / 2) * " "
			else:
				return text + (self.columns - len(text)) * " "
		else:
			return text

	def set_text(self, text, align='l'):
		self.text_pos = 0
		self.last_marquee_step = self.time.time()

		if len(text) > self.columns:
			self.do_marquee = True
			self.text = text
		else:
			self.do_marquee = False
			# add the needed amount of whitespace
			self.text = self.format_text(text, align)
		self._write_string_()

	def set_text_right(self, text):
		prev_text = self.text.rstrip(' ')

		if len(prev_text) + len(text) > self.columns:
			raise ValueError("Text too long, only " + self.columns + "characters.")
		else:
			self.text = prev_text + (' ' * (self.columns - len(prev_text) - len(text))) + text

	def set_text_left(self, text):
		prev_text = self.text.lstrip(' ')
		if len(prev_text) + len(text) > self.columns:
			raise ValueError("Text too long, only " + self.columns + "characters.")
		else:
			self.text = text + (' ' * (self.columns - len(prev_text) - len(text))) + prev_text

	def clear_text(self):
		self.text = ""

	def _set_position_(self, column):
		if (column >= 0) & (column < self.columns):
			self.lcd.set_position(self.line_number, column)
		else:
			raise ValueError("Column " + column + " does not exist.")

	def _time_for_marquee_(self):
		if (not self.last_marquee_step is None) & self.do_marquee:
			if (self.text_pos == 0) & (self.time.time() - self.last_marquee_step >= self.start_duration):
				self._marquee_step_()
			elif (self.text_pos == (len(self.text) - self.columns)) & \
					(self.time.time() - self.last_marquee_step >= self.end_duration):
				self._marquee_step_()
			elif (self.text_pos > 0) & (self.text_pos < len(self.text) - self.columns) & \
					(self.time.time() - self.last_marquee_step >= self.step_interval):
				self._marquee_step_()

	def _marquee_step_(self):
		if self.do_marquee:
			self.text_pos += 1
			if self.text_pos >= len(self.text) - self.columns + 1:
				self.text_pos = 0
			self.last_marquee_step = self.time.time()

	def _write_string_(self):
		text_to_set = self.text[self.text_pos:(self.columns + self.text_pos)]

		for i in range(0, self.columns):
			if text_to_set[i] != self._current_text_[i]:
				self.lcd.write_char_at(self.line_number, i, text_to_set[i])

		self._current_text_ = text_to_set


class TimeLine(LCDLine):

	def __init__(self, lcd, line_number, columns, refresh_interval=0.2, step_interval=1, start_duration=3,
	             end_duration=3):
		super().__init__(lcd, line_number, columns, refresh_interval, step_interval, start_duration, end_duration)

		self.start_time = self.time.time()

		self.update_time()

	def run_every(self):
		self.update_time()
		super().run_every()

	def update_time(self):
		self.clear_text()

		self.set_text_left(self.time.strftime('%H:%M:%S'))

		self.set_text_right(self.time.strftime("%H:%M:%S", self.time.gmtime(self.time.time() - self.start_time)))


class MPDLine(LCDLine):
	from mpd import MPDClient

	def __init__(self, lcd, line_number, columns, key, refresh_interval=0.5, step_interval=1, start_duration=5,
	             end_duration=5, query_info_interval=5, align='l'):
		super().__init__(lcd, line_number, columns, refresh_interval, step_interval, start_duration, end_duration)

		self.client = self.MPDClient()
		self.client.timeout = 10
		self.client.idletimeout = None
		self.client.connect("localhost", 6600)
		self.query_info_interval = query_info_interval
		self.key = key
		self.align = align

	def run_every(self):
		if self.last_marquee_step is None:
			self.update_text(self.align)
		elif self.time.time() - self.last_marquee_step >= self.query_info_interval:
			self.update_text(self.align)

		super().run_every()

	def update_text(self, align):
		new_text = self.format_text(self.client.currentsong()[self.key], align)

		if self.text != new_text:
			self.set_text(new_text, align)