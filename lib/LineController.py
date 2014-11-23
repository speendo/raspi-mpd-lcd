__author__ = 'marcel'

import threading


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
		# last marquee step
		self.last_marquee_step = None
		# current text
		self._current_text = self.columns * " "
		# Status
		self.lock = threading.RLock()

	def run_every(self):
		self.lock.acquire()
		try:
			self._time_for_marquee()
			self._write_string()
			threading.Timer(self.refresh_interval, self.run_every).start()
		finally:
			self.lock.release()

	def resume(self):
		self._current_text = self.columns * ' '
		self.clear_text()

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
		self._write_string()

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
		self.text_pos = 0

	def _set_position(self, column):
		if (column >= 0) & (column < self.columns):
			self.lcd.set_position(self.line_number, column)
		else:
			raise ValueError("Column " + column + " does not exist.")

	def _time_for_marquee(self):
		if (self.last_marquee_step is not None) & self.do_marquee:
			if (self.text_pos == 0) & (self.time.time() - self.last_marquee_step >= self.start_duration):
				self._marquee_step()
			elif (self.text_pos == (len(self.text) - self.columns)) & \
					(self.time.time() - self.last_marquee_step >= self.end_duration):
				self._marquee_step()
			elif (self.text_pos > 0) & (self.text_pos < len(self.text) - self.columns) & \
					(self.time.time() - self.last_marquee_step >= self.step_interval):
				self._marquee_step()

	def _marquee_step(self):
		if self.do_marquee:
			self.text_pos += 1
			if self.text_pos >= len(self.text) - self.columns + 1:
				self.text_pos = 0
			self.last_marquee_step = self.time.time()

	def _write_string(self):
		text_to_set = self.text[self.text_pos:(self.columns + self.text_pos)]
		for i in range(0, self.columns):
			if text_to_set[i] != self._current_text[i]:
				self.lcd.write_char_at(self.line_number, i, text_to_set[i])

		self._current_text = text_to_set


class TimeLine(LCDLine):

	def __init__(self, lcd, line_number, **kwargs):
		super().__init__(lcd, line_number, **kwargs)

		self.start_time = self.time.time()

		self.update_time()

	def run_every(self):
		self.lock.acquire()
		try:
			self.update_time()
			super().run_every()
		finally:
			self.lock.release()

	def resume(self):
		super().resume()
		self.start_time = self.time.time()

	def update_time(self):
		self.clear_text()

		self.set_text_left(self.time.strftime('%H:%M:%S'))

		self.set_text_right(self.time.strftime("%H:%M:%S", self.time.gmtime(self.time.time() - self.start_time)))


class TextLine(LCDLine):
	def __init__(self, lcd, line_number, **kwargs):
		self.align = 'l'
		self.query_info_interval = 5.0
		self.last_update = None
		super().__init__(lcd, line_number, **kwargs)

	def run_every(self):
		self.lock.acquire()
		try:
			if self.last_update is None:
				self.update_text()
			elif self.time.time() - self.last_update >= self.query_info_interval:
				self.update_text()

			super().run_every()
		finally:
			self.lock.release()

	def resume(self):
		super().resume()
		self.last_update = None

	def update_text(self):
		raise NotImplementedError("This is an abstract class (update_text() must be implemented in subclass)")


class MPDLine(TextLine):
	from mpd import MPDClient

	def __init__(self, lcd, line_number, key, **kwargs):
		super().__init__(lcd, line_number, **kwargs)

		self.client = self.MPDClient()
		self.client.timeout = 10
		self.client.connect("localhost", 6600)
		self.key = key

	def update_text(self):
		new_text = self.format_text(self.client.currentsong()[self.key], self.align)

		if self.text != new_text:
			self.set_text(new_text, self.align)
			self.text_pos = 0

		self.last_update = self.time.time()


class FetchLine(TextLine):
	from urllib import request

	def __init__(self, lcd, line_number, url, **kwargs):
		super().__init__(lcd, line_number, **kwargs)
		self.query_info_interval = 60.0
		self.decode = 'latin1'

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
		self.last_update = self.time.time()
