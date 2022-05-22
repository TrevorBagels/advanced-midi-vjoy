from signal import getsignal
from .prodict import Prodict
import json, ctypes, sys, os, time, traceback, colorama

from .core import midi, vjoy
from .core.repconfig import RepConfig, Entry
from dev.core import repconfig


class Main():
	def __init__(self):
		self.midi = midi.Midi()
		self.cfg = RepConfig()
		self.cfg.interpret("DCS.conf")
		virtual_controller_ids = []
		self.instruments = [] #!later we need to make each instrument have its own thread.
		for x in self.cfg.data:
			if x.joystick not in virtual_controller_ids: virtual_controller_ids.append(x.joystick)
			if x.midi not in self.instruments: self.instruments.append(x.midi)
		self.vjoy = vjoy.Vjoy(vids=virtual_controller_ids, useless=True)
		print("\n")
		self.signals = {}
		self.setup_compiled_signal_config()
		self.print_cfg()

		print("\n\nInitialized")
		#print(self.midi.devices())
		#self.midi.run_test()
		#self.midi.finish()
		self.main_loop()

	def setup_compiled_signal_config(self):
		#look for conflicts and warn the user
		"""used_inputs = []
		for x in self.cfg.data:
			button = str(x.joystick) + "/" + str(x.joystick_input)
			if button in used_inputs:
				print("Warning (" + x.name +"): Joystick #" + str(x.jotstick) + " and button/axis #" + str(x.joystick_input), "are already in use.")
		"""

		#some entries say things like "midi_type: NOTE instead of NOTE_ON or NOTE_OFF. "
		for x in self.cfg.data:
			if x.midi_type == "NOTE" and x.behavior == "auto": #create NOTE_ON and NOTE_OFF versions of this
				a = Entry.from_dict(x.copy())
				a.midi_type = "NOTE_ON"
				a.behavior = "press"
				b = Entry.from_dict(x.copy())
				b.midi_type = "NOTE_OFF"
				b.behavior = "release"
				self.cfg.data += [a, b]

		for x in self.cfg.data:
			midi_type = x.midi_type
			pth = x.midi + "/" + str(x.midi_channel) + "/" + midi_type + "/" + str(x.midi_pitch)
			self.signals[pth] = x
		

	def get_signal_config(self, signal:midi.MidiSignal, instrument:str) -> repconfig.Entry:
		pth = instrument + "/" + str(signal.channel) + "/" + signal.signal_type + "/" + str(signal.pitch)
		if pth in self.signals:
			return self.signals[pth]
		else:
			return None

	def print_cfg(self):
		for x in self.cfg.data:
			print(x["name"])
			keys = list(x.keys())
			for a in sorted(keys):
				if a != "name": print("\t", a + ":", x[a])

	def process_signal(self, signal:midi.MidiSignal, instrument:str):
		signal_entry = self.get_signal_config(signal, instrument)
		if signal_entry == None:
			return
		print(signal_entry.name)
		if signal_entry.behavior == "press":
			self.vjoy.SetButton(signal_entry.joystick, 1, signal_entry.joystick_input)
		elif signal_entry.behavior == "release":
			self.vjoy.SetButton(signal_entry.joystick, 0, signal_entry.joystick_input)
		elif signal_entry.behavior == "pulse":
			self.vjoy.SetButton(signal_entry.joystick, 1, signal_entry.joystick_input)
			time.sleep(signal_entry.pulselength)
			self.vjoy.SetButton(signal_entry.joystick, 0, signal_entry.joystick_input)
		elif signal_entry.behavior == "axis":
			pass
		elif signal_entry.behavior == "knob":
			value = signal.value
			if value >= 65: value = value - 64 	#(1 to 7)
			if value < 65: value = -value		#(-1 to -7)
			button = signal_entry.joystick_input
			if value < 0: button = signal_entry.alt_joystick_input
			self.vjoy.SetButton(signal_entry.joystick, 1, button)
			time.sleep(.009 * abs(value))
			self.vjoy.SetButton(signal_entry.joystick, 0, button)
		elif signal_entry.behavior == "tri-switch":
			pos = 1
			if signal.value > 112:
				pos = 2
			elif signal.value < 15:
				pos = 0
			buttons = [signal_entry.joystick_input, signal_entry.alt_joystick_input, signal_entry.third_joystick_input]
			self.vjoy.SetButton(signal_entry.joystick, 1, buttons[pos])
			time.sleep(.01)
			self.vjoy.SetButton(signal_entry.joystick, 0, buttons[pos])
			
			


	def main_loop(self):
		device = self.midi.get_device(self.instruments[0])

		while True:
			while device.poll():
				signal = self.midi.get_signal(device.read(1))
				print(signal)
				self.process_signal(signal, self.instruments[0])
			time.sleep(.05)
		
		self.midi.finish()