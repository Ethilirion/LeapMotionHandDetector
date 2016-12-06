import os, sys, inspect, thread, time, copy, math, subprocess

# to xml parse
import xml.etree.ElementTree as ET

# to log
import logging
logging.basicConfig(filename='log/LMHD.log',level=logging.DEBUG)

#to emit sounds
from multiprocessing import Pool
import winsound

from datetime import datetime

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))

arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
root_dir = '../lib' if sys.maxsize > 2**32 else '../lib'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, root_dir)))

import Leap

from modules.Wrapper import HandWrapper

Debug = True

class LMHDConfig:
	def __init__(self):
		self.version = 1.0
		self.frequency = 0.15
		self.commands = []
		self.parseFile()
	
	def parseConfigElement(self, configElement):
		for config in configElement:
			if config.tag == "frequency":
				self.frequency = float(config.text)
	
	def parseCommand(self, commandElement):
		try :
			name = "" if "name" not in commandElement.attrib else commandElement.attrib["name"]
			newCommand = HandCommand(name)
			newCommand.stopping = newCommand.stopping if "stopping" not in commandElement.attrib else str(commandElement.attrib["stopping"]).lower() == "true"
			newCommand.max_expectancy_time = newCommand.max_expectancy_time if "max_expectancy_time" not in commandElement.attrib else int(commandElement.attrib["max_expectancy_time"])
			for config in commandElement:
				if config.tag == "steps":
					self.parseSteps(config, newCommand)
				elif config.tag == "exec":
					self.parseExecProgram(config, newCommand)
			self.commands.append(newCommand)
		except :
			logging.error("Misformatted command in config file.")
			logging.error(sys.exc_info())
		
	def parseExecProgram(self, execElement, newCommand):
		programToExec = execElement.attrib["program"]
		newCommandArray = []
		newCommandArray.append(programToExec)
		for argument in execElement:
			if argument.tag == "argument":
				newCommandArray.append(argument.attrib["value"])
		newCommand.register_command(newCommandArray)
	
	def parseSteps(self, stepsElement, newCommand):
		for step in stepsElement:
			if step.tag == "step":
				newCommand.addPositions(step.text)
	
	def parseFile(self):
		tree = ET.parse("config.xml")
		root = tree.getroot()
		for children in root:
			if children.tag == "config":
				self.parseConfigElement(children)
			elif children.tag == "command":
				self.parseCommand(children)

class HandCommand:
	def addPositions(self, *positions_array):
		for position in positions_array:
			self.positions.append(position)
	
	def reinit(self):
		self.validated = False
		self.current = -1
		self.last_time_checked = 0
	
	def __str__(self):
		list = ""
		for position in self.positions:
			list = list + "\r\n" + position
		list = list + "\r\nValidated :\t" + str(self.validated)
		list = list + "\r\nWaiting Item :\t[" + str(self.current+ 1) + "]" + str(self.positions[self.current + 1])
		list = list + "\r\nCommand : " + str(self.command)
		list = list + "\r\nStopping : " + str(self.stopping)
		list = list + "\r\nMax expectancy time : " + str(self.max_expectancy_time)
		return list
	
	def advance_in_command(self):
		if (self.current == -1):
			beep_for_position("0x1")
		elif (self.current == 0):
			beep_for_position("0x2")
		elif (self.current == 1):
			beep_for_position("0x3")
		elif (self.current == 2):
			beep_for_position("0x4")
		elif (self.current == 2):
			beep_for_position("0x5")
		else:
			beep_for_position("0x6")
	
		self.current = self.current + 1
		dt = datetime.now()
		self.last_time_checked = int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0))
		
		if (self.current == len(self.positions) - 1):
			self.validated = True
	
	def elapsed_positions(self, elapsed_positions):
		dt = datetime.now()

		max_expectancy_time = self.max_expectancy_time
		if (self.last_time_checked != 0 and (int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0)) - self.last_time_checked) > max_expectancy_time):
			self.reinit()
			return
		if (self.validated == True):
			self.exec_command()
			self.reinit()
			return
		for position in elapsed_positions:
			if (self.positions[self.current + 1] == position):
				self.advance_in_command()
				return
	
	# ex : explorer to Z:\VFAC
	# self.register_command(['explorer.exe', 'Z:\VFAC'])
	def register_command(self, commands):
		self.command = commands
	
	def command_to_string(self) :
		stringCommand = ""
		for command in self.command:
			if (stringCommand != ""):
				stringCommand = stringCommand + " "
			stringCommand = stringCommand + command
		return stringCommand
		
	def exec_command(self):
		if (self.command == []) :
			return
		beep_for_position("RS")
		logging.info('Executed command')
		logging.info(self.positions)
		
		try :
			if (self.stopping == True) :
				subprocess.call(self.command)
			else:
				subprocess.Popen(self.command)
		except :
			beep_for_position("BUG")
	
	def __init__(self, name):
		self.validated = False
		self.command = []
		self.positions = []
		self.current = -1
		self.last_time_checked = 0
		self.name = name
		self.stopping = False
		self.max_expectancy_time = 3000 #default

def beep_for_position(position) :
	Dur = 200 # Set Duration To 1000 ms == 1 second
	if (position == "A") :
		Freq = 400
	elif (position == "B") :
		Freq = 50
	elif (position == "C") :
		Freq = 600
	elif (position == "D") :
		Freq = 700
	elif (position == "E") :
		Freq = 800
	elif (position == "REG") :
		Freq = 900
	elif (position == "FIST") :
		Freq = 1000
	elif (position == "KH") :
		Freq = 1100
	elif (position == "FV") :
		Freq = 1200
	elif (position == "RS") :
		Freq = 1300
	elif (position == "BUG") :
		Freq = 3400
		Dur = 500
	elif (position == "0x1"):
		Freq = 2000
	elif (position == "0x2"):
		Freq = 2200
	elif (position == "0x3"):
		Freq = 2400
	elif (position == "0x4"):
		Freq = 2600
	elif (position == "0x5"):
		Freq = 2800
	elif (position == "0x6"):
		Freq = 3000
	else :
		return
	winsound.Beep(Freq, Dur)

def main():
	try:
		Continue = True
		pool = Pool(processes=1)
		
		config = LMHDConfig()
		
		controller = Leap.Controller()
		#allow program to run in background
		backgroundModeAllowed = controller.config.get("background_app_mode") == 2
		if not backgroundModeAllowed:
			controller.config.set("background_app_mode", 2)
			controller.config.save()
			current = controller.policy_flags
			augmented = current & (1 << 15)
			controller.set_policy_flags(augmented)
			augmented = augmented & (1 << 23)
			controller.set_policy_flags(augmented)
		controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
		
		# built in commands
		exitCommand = HandCommand("exit")
		exitCommand.addPositions("C", "A", "C", "E")
		
		readConfig = HandCommand("readConfig")
		readConfig.addPositions("FIST", "A", "FIST", "A")
		#readConfig.register_command(["notepad", "test.txt"])

		while (Continue == True):
		
			Continue = True
			
			time.sleep(config.frequency);
			frame = controller.frame()
			
			handlist = frame.hands
			
			if (Debug == True) :
				logging.info('>>>>>>>>>>>>>>>')
				dt = datetime.now()
				logging.info('Time :' + str(dt.hour) + ":" + str(dt.minute) + ":" + str(dt.second) + ":" + str(dt.microsecond))
				logging.info(int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0)))
				logging.info('Frame : ' + str(frame))
				logging.info('Handlist : ' + str(handlist))
				logging.info('Handlist empty : ' + str(handlist.is_empty))
		
			if handlist.is_empty:
				logging.info('<<<<<<<<<<<<<<<')
				continue
			
			hand = HandWrapper(handlist[0])
			
			if (Debug == True) :
				logging.info('Hand : ' + str(hand))
				logging.info('Pos A : '+ str(hand.position_a()))
				logging.info('Pos B : '+ str(hand.position_b()))
				logging.info('Pos C : '+ str(hand.position_c()))
				logging.info('Pos D : '+ str(hand.position_d()))
				logging.info('Pos E : '+ str(hand.position_e()))
				logging.info('Pos REG : '+ str(hand.position_regular()))
				logging.info('Pos FIST : '+ str(hand.position_fist()))
				logging.info('Pos KH : '+ str(hand.position_king_hand()))
				logging.info('Pos FV : '+ str(hand.position_flat_v()))
				logging.info('Pos RS : '+ str(hand.position_reverse_spiderman()))
				logging.info('<<<<<<<<<<<<<<<')
			
			## positions logic
			positions = []
			if (hand.position_a()):
				positions.append("A")
			if (hand.position_b()):
				positions.append("B")
			if (hand.position_c()):
				positions.append("C")
			if (hand.position_d()):
				positions.append("D")
			if (hand.position_e()):
				positions.append("E")
			if (hand.position_regular()):
				positions.append("REG")
			if (hand.position_fist()):
				positions.append("FIST")
			if (hand.position_king_hand()):
				positions.append("KH")
			if (hand.position_flat_v()):
				positions.append("FV")
			if (hand.position_reverse_spiderman()):
				positions.append("RS")
			if (hand.position_chinese_eight()):
				positions.append("C8")
			if (hand.position_fake_phone()):
				positions.append("FP")
			if (hand.position_devil_head()):
				positions.append("DH")
			if (hand.position_pinky()):
				positions.append("PP")
			if (hand.position_thumb()):
				positions.append("PT")
			if (hand.position_flat_gun()):
				positions.append("FG")
			
			for handCommand in config.commands:
				handCommand.elapsed_positions(positions)
			
			## commands execution logic
			exitCommand.elapsed_positions(positions)
			if (exitCommand.validated == True):
				beep_for_position("0x1")
				Continue = False
			
			readConfig.elapsed_positions(positions)
			if (readConfig.validated == True):
				beep_for_position("0x2")
				config = LMHDConfig()
	except :
		logging.debug('Program stopped unexpectedly')
		logging.debug(sys.exc_info())
		
if __name__ == "__main__":
	if (Debug == True) :
		logging.info('Program starting')
	main()
	if (Debug == True) :
		logging.info('Program ending')
