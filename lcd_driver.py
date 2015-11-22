# -*- coding: utf-8 -*-
import i2c_lib
from time import sleep

import locale_class

### BIT PATTERNS ###

# Commands
LCD_CLEARDISPLAY =        0b00000001
LCD_RETURNHOME =          0b00000010
LCD_ENTRYMODESET =        0b00000100
LCD_DISPLAYCONTROL =      0b00001000
LCD_CURSORSHIFT =         0b00010000
LCD_FUNCTIONSET =         0b00100000
LCD_SETCGRAMADDR =        0b01000000
LCD_SETDDRAMADDR =        0b10000000

# Flags for display entry mode
LCD_ENTRYRIGHT =          0b00000000
LCD_ENTRYLEFT =           0b00000010
LCD_ENTRYSHIFTINCREMENT = 0b00000001
LCD_ENTRYSHIFTDECREMENT = 0b00000000

# Flags for display on/off control
LCD_DISPLAYON =           0b00000100
LCD_DISPLAYOFF =          0b00000000
LCD_CURSORON =            0b00000010
LCD_CURSOROFF =           0b00000000
LCD_BLINKON =             0b00000001
LCD_BLINKOFF =            0b00000000

# Flags for display/cursor shift
LCD_DISPLAYMOVE =         0b00001000
LCD_CURSORMOVE =          0b00000000
LCD_MOVERIGHT =           0b00000100
LCD_MOVELEFT =            0b00000000

# Flags for function set
LCD_8BITMODE =            0b00010000
LCD_4BITMODE =            0b00000000
LCD_2LINE =               0b00001000
LCD_1LINE =               0b00000000
LCD_5x10DOTS =            0b00000100
LCD_5x8DOTS =             0b00000000

### Bits ###

RS_ON  = 0b00000001 # send command (instead of char)
RS_OFF = 0b00000000

RW_ON  = 0b00000010
RW_OFF = 0b00000000

EN_ON  = 0b00000100
EN_OFF = 0b00000000

BL_ON  = 0b00001000
BL_OFF = 0b00000000

class LCD(object):
	def __init__(self, address = 0x27, default_sleep_time = 0.00004, backlight = True, locale = None):
		# backlight mode
		# we have to start with that as it is required for the following commands
		self.backlight_bit = BL_OFF
		if backlight:
			self.backlight_bit = BL_ON
		
		if locale is None:
			self.locale = LocaleClass.LocaleClass()
		else:
			self.locale = locale

		self.bus = i2c_lib.i2c_device(address)
		self.default_sleep_time = default_sleep_time
		
		# init LCD with 4 bit
		self.init_4_bit()
		
		# define custom chars
		self.def_custom_chars()
		
		# init LCD mode
		self.init_display_mode()
		
	def init_4_bit(self):
		sleep(0.015) # wait 150 ms
		self.write_cmd(0b00000011)
		sleep(0.0041) # wait 4,1 ms
		self.write_cmd(0b00000011)
		sleep(0.0001) # wait 100 µs
		self.write_cmd(0b00000011)
		# set to 4 bit mode now
		self.write_cmd(0b00000010)
	
	def init_display_mode(self):
		# 2 lines, 5x8 dots
		self.write_cmd(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		# turn display off
		self.write_cmd(LCD_DISPLAYCONTROL | LCD_DISPLAYOFF)
		# clear display
		self.clear_display()
		# cursor move right, no shift
		self.write_cmd(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
		# turn display on
		self.write_cmd(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF)
	
	def def_custom_chars(self):
		# raise error if too many custom characters are defined
		if (len(self.locale.custom_chars) > 8):
			raise ValueError("Too many custom characters (only 8 allowed)!")
		
		# define the index of the custom chars
		custom_char_index = 0
		
		# set "cursor" at the start of the CGRAM
		pos = LCD_SETCGRAMADDR | 0b0000000 # this is the start of the CGRAM
		self.write_cmd(pos)
		
		# write custom characters to CGRAM
		for c in self.locale.custom_chars.keys():
			char_shape = self.locale.custom_chars[c]
			
			if len(char_shape) != 8:
				raise ValueError("One of the custom chars is not defined correctly. Each custom char must consist of 8 bytes (representing 8 lines).")
			
			# store shape in CGRAM
			for b in char_shape:
				self.write_byte(b, rs = RS_ON)
			
			# store defined char to custom_chars dict
			self.locale.locale_chars[c] = custom_char_index
			custom_char_index += 1
	
	def clear_display(self):
		# usually a longer sleep time is required
		self.write_cmd(LCD_CLEARDISPLAY, sleep_time = 0.0007) # for my display it takes about 7000 ms - please check for your display
	
	def set_position(self, line, column):
		# position commands always have the first bit set (1xxxxxxx)
		pos = int(LCD_SETDDRAMADDR)
		
		# first set the line
		line_pos = 0
		if line == 1:
			line_pos = 0
		elif line == 2:
			line_pos = 64
		elif line == 3:
			line_pos = 20
		elif line == 4:
			line_pos = 84
		
		# now set the column
		pos += line_pos + column
		
		# write it to the display
		self.write_cmd(pos)
	
	def backlight(self, state):
		if state:
			self.backlight_bit = BL_ON
		else:
			self.backlight_bit = BL_OFF
	
	def replace_locale_chars(self, char):
		if char in self.locale.locale_chars:
			return self.locale.locale_chars[char]
		else:
			return ord(char)

	def write_byte(self, byte, rs, sleep_time = None):
		if sleep_time is None:
			sleep_time = self.default_sleep_time

		# write high nibble
		self.send_nibble(nibble = byte & 0b11110000, rw = RW_OFF, rs = rs)
		# write low nibble
		self.send_nibble(nibble = (byte << 4) & 0b11110000, rw = RW_OFF, rs = rs)
		sleep(sleep_time) # sleep (default 40 µs)
		
	def send_nibble(self, nibble, rw, rs):
		# bits:
		# cccc bl en rw rs
		# cccc: nibble (4 bits)
		# bl (backlight, 1 bit, low: off, high: on)
		# en (1 bit, sequence: high - low - high)
		# rw (1 bit, low: write, high: read)
		# rs (1 bit, low: command, high: character)
		self.bus.write(nibble | EN_ON | rw | rs | self.backlight_bit) # enable high
		self.bus.write(nibble | EN_OFF | rw | rs | self.backlight_bit) # enable low
	
	def write_cmd(self, cmd, sleep_time = None):
		self.write_byte(cmd, rs = RS_OFF, sleep_time = sleep_time)
	
	def write_char(self, char):
		char_number = self.replace_locale_chars(char)
		self.write_byte(char_number, rs = RS_ON)
	
	def write(self, string):
		for c in string:
			self.write_char(c)
