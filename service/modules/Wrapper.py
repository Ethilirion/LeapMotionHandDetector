import Leap, math

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

	# thumb, index and pinky extended, hand about flat, all other fingers are folded
	def position_reverse_spiderman(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_PINKY)):
			return True
		return False
	
	# thumb and index are extended, hand about flat, all other fingers are folded
	def position_chinese_eight(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_INDEX)):
			return True
		return False
	
	# thumb and pinky are extended, hand about flat, all other fingers are folded
	def position_fake_phone(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_PINKY)):
			return True
		return False
		
	#  middle finger is extended, hand about flat, all other fingers are folded
	def position_reverse_middle(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_MIDDLE)):
			return True
		return False
	
	# index and pinky are extended, hand about flat, all other fingers are folded
	def position_devil_head(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_PINKY)):
			return True
		return False
	
	# pinky is extended, hand about flat, all other fingers are folded
	def position_pinky(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_PINKY)):
			return True
		return False
	
	# thumb is extended, hand about flat, all other fingers are folded
	def position_thumb(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB)):
			return True
		return False
	
	# thumb, index and middle fingers are extended, hand about flat, all other fingers are folded
	def position_flat_gun(self):
		if (self.is_about_flat() and self.specific_fingers_extended(Leap.Finger.TYPE_THUMB, Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE) and self.fingers_jointed(Leap.Finger.TYPE_INDEX, Leap.Finger.TYPE_MIDDLE)):
			return True
		return False
