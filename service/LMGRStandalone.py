import os, sys, inspect, thread, time, subprocess, collections
from multiprocessing import Pool
from datetime import datetime

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))

arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
root_dir = '../lib' if sys.maxsize > 2**32 else '../lib'

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, root_dir)))

import Leap


# to log
import logging
logging.basicConfig(filename='LMGR.log',level=logging.DEBUG)

class GestureInfo(Leap.SwipeGesture):
	def __init__(self, gesture):
		Leap.SwipeGesture.__init__(self, gesture)
		dt = datetime.now()
		self.update_time = int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0))
	
class SwipeGestureListener(Leap.Listener):
	def __init__(self):
		Leap.Listener.__init__(self)
		self.current_gesture = None
		self.gesture_history = collections.deque([], 10) #appendleft => add at top, pop => remove from bottom
	
	def manage_command(self, frame) :
		#if direction left, do smthng
		#if direction right, do smthng
		print (frame.direction)
		return
	
	def is_new_gesture(self, current_gesture):
		#first gesture ever
		if (type(self.current_gesture) == type(None)):
			self.current_gesture = current_gesture
			self.manage_command(current_gesture)
			return
		
		last_used_gesture = self.gesture_history[0] if len(self.gesture_history) > 0 else None
		dt = datetime.now()
		current_time = int(round(time.time(),0)) * 1000 + int(round(dt.microsecond / 1000.0, 0))

		if ((current_time - self.current_gesture.update_time) < 200) :
			self.current_gesture.update_time = current_time
		else:
			self.gesture_history.appendleft(self.current_gesture)
			self.current_gesture = current_gesture
			self.manage_command(current_gesture)
	
	def on_connect(self, controller):
		print ("Connected")

	def on_frame(self, controller):
		#print ("Frame available")
		frame = controller.frame()

		for gesture in frame.gestures():
			if gesture.type is Leap.Gesture.TYPE_SWIPE:
				swipe = Leap.SwipeGesture(gesture)
				current_gesture = GestureInfo(swipe)
				self.is_new_gesture(current_gesture)

def main():
	try:
		pool = Pool(processes=1)
		
		# Create a sample listener and controller
		listener = SwipeGestureListener()
		controller = Leap.Controller()
		
		# config :
		# Gesture.Swipe.MinLength (def : 150)
		# Gesture.Swipe.MinVelocity (def : 1000 mm/s)
		# ex : controller.config.set("Gesture.Swipe.MinLength", 200.0)
		controller.enable_gesture(Leap.Gesture.TYPE_SWIPE, True)
		controller.config.set("Gesture.Swipe.MinLength", 100.0)
		controller.config.set("Gesture.Swipe.MinVelocity", 1000.0)
		controller.config.save()
		# Have the sample listener receive events from the controller
		controller.add_listener(listener)

		# Keep this process running until Enter is pressed
		print "Press Enter to quit..."
		try:
			sys.stdin.readline()
		except KeyboardInterrupt:
			pass
		finally:
			# Remove the sample listener when done
			controller.remove_listener(listener)

	except :
		logging.debug('Program stopped unexpectedly')
		logging.debug(sys.exc_info())

if __name__ == "__main__":
	main()
	