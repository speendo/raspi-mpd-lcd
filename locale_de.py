# -*- coding: utf-8 -*-

from .locale_class import LocaleClass

class LocaleDE(LocaleClass):
	def __init__(self):
		self.locale_chars = {
			'ä': 225,
			'ß': 226,
			'ö': 239,
			'ü': 245
		}
		
		# up to 8 5x8 custom chars
		self.custom_chars = {
			'Ä': [
				0b00001010,
				0b00000000,
				0b00001110,
				0b00010001,
				0b00011111,
				0b00010001,
				0b00010001,
				0b00000000
			],
			'Ö': [
				0b01010,
				0b00000,
				0b01110,
				0b10001,
				0b10001,
				0b10001,
				0b01110,
				0b00000
			],
			'Ü': [
				0b01010,
				0b00000,
				0b10001,
				0b10001,
				0b10001,
				0b10001,
				0b01110,
				0b00000
			]
		}
