import ctypes, os



class Vjoy:
	def __init__(self, vids=[1], useless=False):
		self.useless = useless
		if useless == False: #because i like to program on my mac, and this is windows only
			import winreg
			try:
				# Load the vJoy library
				# Load the registry to find out the install location
				vjoyregkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{8E31F76F-74C3-47F1-9550-E041EEDC5FBB}_is1')
				installpath = winreg.QueryValueEx(vjoyregkey, 'InstallLocation')
				winreg.CloseKey(vjoyregkey)
				#print(installpath[0])
				dll_file = os.path.join(installpath[0], 'x64', 'vJoyInterface.dll')
				self.vjoy = ctypes.WinDLL(dll_file)
				
				
				# Getting ready
				for vid in vids:
					print('Acquiring vJoystick:', vid)
					assert(self.vjoy.AcquireVJD(vid) == 1)
					assert(self.vjoy.GetVJDStatus(vid) == 0)
					self.vjoy.ResetVJD(vid)
			except:
				#traceback.print_exc()
				print('Error initializing virtual joysticks')
				return
	#'X', 'Y', 'Z', 'RX', 'RY', 'RZ', 'SL0', or 'SL1'.
	def SetAxis(self, joystick:int, value:int, axis):
		if self.useless:
			print("controller #" + str(joystick) + "-" + axis + ":", value)
		else:
			self.vjoy.SetAxis((value + 1) << 8, joystick, axis)
	def SetButton(self, joystick:int, value:int, ID:int):
		if self.useless:
			print("controller #" + str(joystick) + "-B" + str(ID) + ":", value)
		else:
			self.vjoy.SetBtn(value, joystick, ID)

