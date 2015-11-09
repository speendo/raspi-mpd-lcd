import smbus
#from time import sleep

class i2c_device:
	def __init__(self, address, port=1):
		self.address = address
		self.bus = smbus.SMBus(port)
		# self.sleep_time = 0.0001
		
	def write(self, cmd):
		self.bus.write_byte(self.address, cmd)
		# sleep(self.sleep_time)
#		print('{0:08b}'.format(cmd, 'b'))
#		sleep(0.01)
	
	def read(self):
		return self.bus.read_byte(self.address)
