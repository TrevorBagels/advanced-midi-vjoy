


from ..prodict import Prodict

class Property(Prodict):
	name:			str
	type:			any #int, bool, str
	default:		any
	optional:		bool #if true, this property won't be added to anything automatically.
	auto_update:	bool #when this property is assigned for something, anything without this property assigned will use the last assigned value.
	def init(self):
		self.type 			= str
		self.default 		= None
		self.optional		= False
		self.auto_update	= False

class Entry(Prodict):
	name:			str
	joystick:		int
	joystick_input:	str
	midi:			str
	midi_channel:	int
	midi_pitch:		int
	midi_type:		str
	behavior:		str

	pulselength:	float
	alt_joystick_input:		str
	third_joystick_input:	str


class RepConfig:
	def __init__(self):
		#start reading the file
		self.data:list[Entry] = []
		self.properties:dict[str, Property] = {}

	def parse_lines(self, lines):
		parsed = []
		for x in lines:
			#remove any comments from the line, or trailing whitespace
			x = x.split("#")[0].strip(" ")
			if x.strip() != "":
				parsed.append(x)
		#print("\n".join(parsed))
		return parsed

	def interpret_property_lines(self, lines):
		p = Property(name=lines[0].split(" ", 1)[1])
		_p = {"auto_update": "0", "type": "str"}
		for line in lines[1:]:
			data = line.split(" ", 1)
			_p[data[0]] = data[1]
		
		p.auto_update = bool(int(_p["auto_update"]))
		types = {"str": str, "int": int, "bool": bool, "float": float}
		p.type = types[_p["type"]]
		if "default" in _p: p.default = _p["default"]
		self.properties[p.name] = p
		

	def interpret_entry_lines(self, lines):
		entry = Entry(name = lines[0])
		_e = {}
		for x in self.properties:
			if self.properties[x].optional == False:
				_e[x] = self.properties[x].default

		for line in lines[1:]:
			data = line.split(" ", 1)
			_e[data[0]] = data[1]

		#now go through all the properties in _e and make them the correct types and stuff and add them to the real entry.
		for k, v in _e.items():
			if self.properties[k].auto_update: #update the default value.
				self.properties[k].default = v
			value = v
			p_type = self.properties[k].type
			if p_type == bool: value = bool(int(v))
			if p_type == int: value = int(v)
			if p_type == float: value = float(v)#, type == str just gets left alone, as is.
			entry[k] = value


		self.data.append(entry)




	def interpret(self, file):
		lines = self.parse_lines(open(file, "r").readlines())
		lines.append("@end")
		#go through line by line now.

		last_lines = []

		entries = []

		for i in range(len(lines)):
			if lines[i][0] != "\t" and i != 0: #new top line (line without tab). interpret the last top line/parent, then update the top line.
				entries.append(last_lines.copy())
				last_lines = []
			last_lines.append(lines[i].strip())
		
		for x in entries:
			print(x)
			if x[0].startswith("@end"):
				continue
			elif x[0].startswith("@property"):
				self.interpret_property_lines(x)
			elif x[0].startswith("@default"): #update the default
				values = x[0].split(" ", 2)
				self.properties[values[1]].default = values[2]
			else:
				self.interpret_entry_lines(x)

		
		

