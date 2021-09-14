#https://github.com/yorkrobotlab/pi-puck/blob/master/python-library/pipuck/ft903.py

from smbus2 import SMBus

_FT903_I2C_ADDRESS = 0x1C

class FT903:
	"""Class to interface with the FT903 microcontroller."""

	def __init__(self, bus: SMBus, i2c_address: int = _FT903_I2C_ADDRESS):
		"""
		:param bus: :class:`smbus.SMBus` instance to use for communication
		:param i2c_address: I2C slave address of the FT903 chip (default ``0x1C``)
		"""
		self._i2c_bus = bus
		self._i2c_address = i2c_address

	def write_data_8(self, address, data):
		self._i2c_bus.write_byte_data(self._i2c_address, address, data)

	def write_data_16(self, address, data):
		self._i2c_bus.write_word_data(self._i2c_address, address, data)

	def read_data_8(self, address):
		return self._i2c_bus.read_byte_data(self._i2c_address, address)

	def read_data_16(self, address):
		return self._i2c_bus.read_word_data(self._i2c_address, address)
