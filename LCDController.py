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

		# position
		self.position = (0,0)

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

			# update current position
			self.position = (line, column + 1)

		finally:
			self.lock.release()

	def write_char_at(self, line, column, char):
			self.lock.acquire()
			try:
				if self.position[0] != line | self.position[1] != column:
					self.set_position(line, column)
				self.lcd.writeChar(char)
				self.position = (line, column + 1)
			finally:
				self.lock.release()


class LCDLine(threading.Thread):
	import time
	import math

	def __init__(self, lcd, line_number, **kwargs):
		super().__init__()
		self.lcd = lcd
		self.line_number = line_number

		# kwargs
		self.refresh_interval = 0.5
		self.step_interval = 0.5
		self.start_duration = 3.0
		self.end_duration = 5.0
		self.columns = self.lcd.columns

		for key, value in kwargs.items():
			setattr(self, key, value)

		# current text
		self.text = ""
		# current position
		self.text_pos = 0
		# marquee necessary?
		self.do_marquee = False
		# current text
		self._current_text_ = self.columns * " "
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

		print(text_to_set)

		for i in range(0, self.columns):
			if text_to_set[i] != self._current_text_[i]:
				self.lcd.write_char_at(self.line_number, i, text_to_set[i])

		self._current_text_ = text_to_set


class TimeLine(LCDLine):

	def __init__(self, lcd, line_number, **kwargs):
		super().__init__(lcd, line_number, **kwargs)

		self.start_time = self.time.time()

		self.update_time()

	def run_every(self):
		self.update_time()
		super().run_every()

	def update_time(self):
		self.clear_text()

		self.set_text_left(self.time.strftime('%H:%M:%S'))

		self.set_text_right(self.time.strftime("%H:%M:%S", self.time.gmtime(self.time.time() - self.start_time)))


class TextLine(LCDLine):
	def __init__(self, lcd, line_number, **kwargs):
		self.align = 'l'
		super().__init__(lcd, line_number, **kwargs)

	def run_every(self):
		if self.last_marquee_step is None:
			self.update_text()
		elif self.time.time() - self.last_marquee_step >= self.query_info_interval:
			self.update_text()

		super().run_every()

	def update_text(self):
		raise NotImplementedError("This is an abstract class (update_text() must be implemented in subclass)")

class MPDLine(TextLine):
	from mpd import MPDClient

	def __init__(self, lcd, line_number, key, **kwargs):
		self.query_info_interval = 5.0
		super().__init__(lcd, line_number, **kwargs)

		self.client = self.MPDClient()
		self.client.timeout = 10
		self.client.idletimeout = None
		self.client.connect("localhost", 6600)
		self.key = key

	def update_text(self):
		new_text = self.format_text(self.client.currentsong()[self.key], self.align)

		if self.text != new_text:
			self.set_text(new_text, self.align)


class FetchLine(TextLine):
	from urllib import request

	def __init__(self, lcd, line_number, url, **kwargs):
		self.query_info_interval = 60.0
		self.decode = 'latin1'
		super().__init__(lcd, line_number, **kwargs)

		self.url = url
		self.req = self.request.Request(url)


		self.fetcher = self.Fetcher(self.req, self.decode)
		self.fetcher.start()

	class Fetcher(threading.Thread):
		from urllib import request, error

		def __init__(self, req, decode):
			super().__init__()

			self.text = "NO DATA"

			self.req = req
			self.decode = decode

		def run(self):
			try:
				response = self.request.urlopen(self.req)
				self.text = response.read().decode(self.decode)
			except (self.error.HTTPError, self.error.URLError) as e:
				print(e)

	def update_text(self):
		new_text = self.format_text(self.fetcher.text, self.align)

		if self.text != new_text:
			self.set_text(new_text, self.align)

		self.fetcher.run()
