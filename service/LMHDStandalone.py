import os, sys, inspect, thread, time, copy, math, subprocess

# to xml parse
import xml.etree.ElementTree as ET

# to log
import logging
logging.basicConfig(filename='LMHD.log',level=logging.DEBUG)

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

Debug = True
		
class HandWrapper() :
	def __init__(self, leap_hand) :
		self.hand = leap_hand
	
	############### TOOLS ################
	def print_normal(self):
		normal = self.hand.palm_normal
		print("x :\t" + str(round(normal.x, 5)) + "\ty :\t" + str(round(normal.y, 5)) + "\tz :\t" + str(round(normal.z, 5)))
	
	def __prototype_thumb_angle(self):
		thumb = self.hand.fingers[Leap.Finger.TYPE_THUMB]
		point_a = thumb.bone(Leap.Bone.TYPE_PROXIMAL).prev_joint
		point_b = thumb.bone(Leap.Bone.TYPE_INTERMEDIATE).prev_joint
		point_c = thumb.bone(Leap.Bone.TYPE_INTERMEDIATE).next_joint
		point_d = thumb.bone(Leap.Bone.TYPE_DISTAL).next_joint
		ab = Leap.Vector(point_b.x - point_a.x, point_b.y - point_a.y, point_b.z - point_a.z)
		cd = Leap.Vector(point_d.x - point_c.x, point_d.y - point_c.y, point_d.z - point_c.z)
		dot_product = ab.x * cd.x + ab.y * cd.y + ab.z * cd.z
		magnitude_ab = math.sqrt(pow(ab.x, 2) + pow(ab.y, 2) + pow(ab.z, 2))
		magnitude_cd = math.sqrt(pow(cd.x, 2) + pow(cd.y, 2) + pow(cd.z, 2))
		cos_angle = dot_product / (magnitude_ab * magnitude_cd)
		angle = math.acos(cos_angle)
		return angle
	
	def value_framing(self, vmax, v, vmin):
		if (vmax < v and vmin > v):
			return True
		return False
	
	# fingers 			: 	Leap.Finger[]
	# finger_type_one 	:	Leap.Finger.Type
	# finger_type_two 	:	Leap.Finger.Type
	# bone_type			:	Leap.Bone.Type
	def calculate_bones_distance(self, finger_type_one, finger_type_two, bone_type):
		fingers = self.hand.fingers
		finger_one_bone = fingers[finger_type_one].bone(bone_type)
		finger_two_bone = fingers[finger_type_two].bone(bone_type)
		distance_tip = math.sqrt(pow(finger_two_bone.next_joint.x - finger_one_bone.next_joint.x, 2) + pow(finger_two_bone.next_joint.y - finger_one_bone.next_joint.y, 2) + pow(finger_two_bone.next_joint.z - finger_one_bone.next_joint.z, 2))
		return distance_tip
	
	# fingers 			: 	Leap.Finger[]
	# finger_type_one 	:	Leap.Finger.Type
	# finger_type_two 	:	Leap.Finger.Type
	# bone_type			:	Leap.Bone.Type
	def calculate_bones_distance_different_types(self, finger_type_one, finger_type_two, bone_type_one, bone_type_two):
		fingers = self.hand.fingers
		finger_one_bone = fingers[finger_type_one].bone(bone_type_one)
		finger_two_bone = fingers[finger_type_two].bone(bone_type_two)
		distance_tip = math.sqrt(pow(finger_two_bone.next_joint.x - finger_one_bone.next_joint.x, 2) + pow(finger_two_bone.next_joint.y - finger_one_bone.next_joint.y, 2) + pow(finger_two_bone.next_joint.z - finger_one_bone.next_joint.z, 2))
		return distance_tip
	
	def fingers_jointed_precision(self, finger_type_one, finger_type_two, precision) :
		Regular, Thumb, Pinky = range(3)
		process = Regular
		
		# check if fingers are adjacents
		if (max([finger_type_one, finger_type_two]) - min([finger_type_one, finger_type_two]) != 1):
			return False
		fingers = self.hand.fingers
		
		if not (finger_type_one == 0 or finger_type_one == 4 or finger_type_two == 0 or finger_type_two == 4) :
			first_finger = finger_type_one
			second_finger = finger_type_two
		elif (finger_type_one == 0 or finger_type_two == 0) :
			process = Thumb
			# first finger = thumb
			# second finger = index
			if (finger_type_one == 0):
				first_finger = finger_type_one
				second_finger = finger_type_two
			elif (finger_type_two == 0):
				first_finger = finger_type_two
				second_finger = finger_type_one
		elif (finger_type_one == 4 or finger_type_two == 4) :
			process = Pinky
			# first finger = pinky
			# second finger = ring
			if (finger_type_one == 4):
				first_finger = finger_type_one
				second_finger = finger_type_two
			elif (finger_type_two == 4):
				first_finger = finger_type_two
				second_finger = finger_type_one
		
		if (process == Regular):
			distance_tip_distal = self.calculate_bones_distance(first_finger, second_finger, Leap.Bone.TYPE_DISTAL)
			distance_tip_intermediate = self.calculate_bones_distance(first_finger, second_finger, Leap.Bone.TYPE_INTERMEDIATE)
			distance_tip_proximal = self.calculate_bones_distance(first_finger, second_finger, Leap.Bone.TYPE_PROXIMAL)
			distance_tip_metacarpal = self.calculate_bones_distance(first_finger, second_finger, Leap.Bone.TYPE_METACARPAL)
			avg_distance_tips = distance_tip_distal + distance_tip_intermediate + distance_tip_proximal + distance_tip_metacarpal
			avg_distance = avg_distance_tips / 4
			
		elif (process == Thumb):
			avg_distance = self.calculate_bones_distance_different_types(first_finger, second_finger, Leap.Bone.TYPE_INTERMEDIATE, Leap.Bone.TYPE_METACARPAL)
			if (abs(avg_distance - fingers[first_finger].width) < (4 + precision)) :
				return True
			else:
				return False
			
		elif (process == Pinky):
			distance_close = self.calculate_bones_distance_different_types(first_finger, second_finger, Leap.Bone.TYPE_METACARPAL, Leap.Bone.TYPE_METACARPAL)
			distance_medium = self.calculate_bones_distance_different_types(first_finger, second_finger, Leap.Bone.TYPE_INTERMEDIATE, Leap.Bone.TYPE_PROXIMAL)
			distance_far = self.calculate_bones_distance_different_types(first_finger, second_finger, Leap.Bone.TYPE_DISTAL, Leap.Bone.TYPE_INTERMEDIATE)
			avg_distance = distance_medium + distance_medium + distance_far
			avg_distance = avg_distance / 3
		
		fingers_calculated_width = abs(fingers[first_finger].width / 2 + fingers[second_finger].width / 2)
		if (abs(fingers_calculated_width - avg_distance) < (fingers_calculated_width * 0.2 + precision / 4)):
			return True
		return False
	
	def fingers_jointed(self, finger_type_one, finger_type_two) :
		return self.fingers_jointed_precision(finger_type_one, finger_type_two, 0)
		
	def fingers_about_jointed(self, finger_type_one, finger_type_two) :
		return self.fingers_jointed_precision(finger_type_one, finger_type_two, 2)
	
	def fingers_extended(self):
		for i in self.hand.fingers :
			if (i.is_extended == False):
				return False
		return True
	
	def get_fingers(self):
		return self.hand.fingers
		
	def get_leap_hand(self):
		return self.hand

	########### BASIC POSTURES #####################
	def is_flat(self):
		normal = self.hand.palm_normal
		if (abs(normal.x) < 0.2 and abs(normal.z) < 0.25 and normal.y < 0.):
			return True
		return False
		
	def is_about_flat(self):
		normal = self.hand.palm_normal
		if (abs(normal.x) < 0.3 and abs(normal.z) < 0.45 and normal.y < 0.9):
			return True
		return False
		
	def is_edge(self):
		normal = self.hand.palm_normal
		# right hand edge toward left
		if (self.value_framing(-1.,normal.x,-0.9) and self.value_framing(-0.2,normal.z,0.1)):
			return True
		return False

	def is_about_edge(self):
		normal = self.hand.palm_normal
		# right hand edge toward left
		if (self.value_framing(-1.,normal.x,-0.75) and self.value_framing(-0.35,normal.z,0.1)):
			return True
		return False

	# finger_type : Leap.Finger.Type
	def finger_extended(self, finger_type):	
		if (self.hand.fingers[finger_type].is_extended == False):
			return False
		for i in self.hand.fingers:
			if (i.type != finger_type and i.is_extended == True):
				return False
		return True

	def no_fingers_extended(self):
		for i in self.hand.fingers:
			if (i.is_extended == True):
				return False
		return True

	def all_fingers_jointed(self):
		if self.fingers_about_jointed(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_INDEX) and self.fingers_jointed(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE) and self.fingers_jointed(Leap.Finger.TYPE_MIDDLE, Leap.Finger.TYPE_RING) and self.fingers_jointed(Leap.Finger.TYPE_RING, Leap.Finger.TYPE_PINKY) :
			return True
		return False
			
	def specific_fingers_extended(self, *extended):
		for finger in self.hand.fingers:
			finger_type_has_to_be_extended = False
			for finger_type in extended:
				if (finger.type == finger_type):
					finger_type_has_to_be_extended = True
					break
			if (not finger.is_extended == finger_type_has_to_be_extended):
				return False
		return True
	
	########## POSITIONS ################
	# hand flat and all fingers extended
	def position_regular(self):
		return self.is_flat() and self.fingers_extended()
	
	# hand flat and index extended
	def position_a(self) :
		return self.is_about_flat() and self.finger_extended(Leap.Finger.TYPE_INDEX)

	# hand edgewise and index extended
	def position_b(self):
		return self.is_about_edge() and self.finger_extended(Leap.Finger.TYPE_INDEX)
	
	# hand flat index and middle jointed, pinky and ring jointed, middle and ring not jointed
	def position_c(self):
		index_middle_jointed = self.fingers_jointed(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE)
		middle_ring_jointed = self.fingers_jointed(Leap.Finger.TYPE_MIDDLE, Leap.Finger.TYPE_RING)
		ring_pinky_jointed = self.fingers_jointed(Leap.Finger.TYPE_RING, Leap.Finger.TYPE_PINKY)
		if self.is_about_flat() and index_middle_jointed and ring_pinky_jointed and not middle_ring_jointed:
			return True
		return False
		
	# hand flat all fingers jointed
	def position_d(self):
		if self.is_about_flat() and self.all_fingers_jointed():
			return True
		return False
	
	# hand edge
	def position_e(self):
		if self.is_about_edge():
			return True
		return False

	# fist hand
	def position_fist(self):
		if self.no_fingers_extended():
			return True
		return False
	
	# fingers index and middle are extended and jointed, hand about flat, all other fingers are folded
	def position_king_hand(self):
		if self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE) and self.fingers_jointed(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE):
			return True
		return False
	
	# fingers index and middle are extended and not jointed, hand about flat, all other fingers are folded
	def position_flat_v(self):
		if self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE) and not self.fingers_jointed(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE):
			return True
		return False

	def position_revert_spiderman(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_PINKY)):
			return True
		return False

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
			newCommand = HandCommand(commandElement.attrib["name"])
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

		if (self.last_time_checked != 0 and (int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0)) - self.last_time_checked) > 5000):
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
			
			#time.sleep(0.25);
			time.sleep(0.15);
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
				logging.info('Pos RS : '+ str(hand.position_revert_spiderman()))
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
			if (hand.position_revert_spiderman()):
				positions.append("RS")
			
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
