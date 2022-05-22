import pygame.midi, time
from ..prodict import Prodict
#https://computermusicresource.com/MIDI.Commands.html

class MidiDevice(Prodict):
	interface:		str
	name:			str
	is_input:		bool
	takes_output:	bool
	is_opened:		bool
	index:			int

class MidiSignal(Prodict):
	channel:	int #0-15 (1 - 16)
	signal_type:	str
	pitch:		int #0-127. can also be the button or fader number.
	value:		int #0-127. velocity, value of fader, etc.




class Midi:
	def __init__(self):
		#self.signal_types = {"NOTE_OFF": 128, "NOTE_ON": 144, "POLY_KEY_PRESSURE": 160, "CONTROL_CHANGE": 176,"PROGRAM_CHANGE": 192, "CHANNEL_PRESSURE": 208, "PITCH_BEND": 224, "SYSTEM": 240}
		signal_types = ["NOTE_OFF", "NOTE_ON", "POLY_KEY_PRESSURE", "CONTROL_CHANGE", "PROGRAM_CHANGE", "CHANNEL_PRESSURE", "PITCH_BEND", "SYSTEM"]
		self.status_commands = []
		for x in range(128):
			self.status_commands.append(None)
		for x in signal_types:
			for c in range(16):
				self.status_commands.append( (x, c+1) )

		pygame.midi.init()

	def finish(self):
		pygame.midi.quit()

	def devices(self) -> list[MidiDevice]:
		devices = []
		for i in range(pygame.midi.get_count()):
			inf = pygame.midi.get_device_info(i)
			info = MidiDevice(interface=inf[0].decode(), name=inf[1].decode(), is_input=bool(inf[2]), takes_output=bool(inf[3]), is_opened=bool(inf[4]), index=i)
			devices.append(info)
		return devices
	
	def get_signal(self, data: tuple[tuple[int, int, int, int], int]) -> MidiSignal:
		data = data[0]
		m = MidiSignal(channel=self.status_commands[data[0][0]][1], 
			signal_type=self.status_commands[data[0][0]][0], 
			pitch=data[0][1], value=data[0][2])
		return m

	def get_device(self, name):
		ds = self.devices()
		for x, i in zip(ds, range(len(ds))):
			if x.name == name:
				return pygame.midi.Input(i)

	def run_test(self):
		ds = self.devices()
		for x in ds:
			print(str(x.index) + ").", x.name)
		device_select = int(input("> "))
		print(ds[device_select].name, "selected.")
		device = pygame.midi.Input(device_select)

		while True:
			while device.poll():
				print( self.get_signal(device.read(1)))
			time.sleep(.05)
		
		device.close()

	def read(self, instrument:int):
		return self.get_signal(pygame.midi.Input(instrument).read(1))
		
		



	