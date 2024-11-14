#! /usr/bin/python

import threading #To create a thread in Python, you can use the threading module (high level) or the thread module (low level). 
				 #In general, for thread processing, the threading module implemented on top of the thread module is used, and the thread module is rarely used (deprecated).
import signal
import time
import sys
import os
import random

NR_CONSUMER = 10
NR_PRODUCER = 5#NR_CONSUMER / 2

buffer = [] # Define Empty List
cv = threading.Condition()
exitto = False

class Consumer(threading.Thread):	# threading.Thread is super class
	def __init__(self, threadID, name='None', counter=0, *args):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.args = args
		
	def run(self):
		#print('******************************************************')
		print(f'Consumer thread[{self.threadID}] is run')
		#print('******************************************************')
		#for x in range(5):
		continuex = True
		while continuex :#len(buffer) < 1:
			cv.acquire()
			
			print('******************************************************')
			if not buffer and exitto == False: #if not buffer:
				print(f'Consumer thread[{self.threadID}] waiting...')
				cv.wait()
			
			if exitto:
				continuex = False
				print('Consumer is exit...')
				#print('******************************************************')
				cv.release()
				break				
			else:
				if buffer:
					bufferV = buffer.pop(0)
					print(f'Consumer buffer is {bufferV}')
				else :
					print('Consumer buffer is empty')
					
				print('******************************************************')
				cv.release()
				
			#time.sleep(0.01)
			
		print('Consumer return run')
				
class Producer(threading.Thread):
	def __init__(self, threadID, name='None', counter=0, *args):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.args = args
		
	def run(self):
		#print('******************************************************')
		print(f'Producer thread[{self.threadID}] is run')
		#print('******************************************************')
		for i in range(10): #while True :
			
			cv.acquire()
			print(f'Producer i is {i}')
			randomNumber = random.randrange(0, 20)
			buffer.append(randomNumber)
			cv.notify()
			print(f'Producer thread[{randomNumber}] is Notify!!!')
			cv.release()
			time.sleep(0.05)
				
		print('Before Producer return run')
		cv.acquire()
		exitto = True
		#cv.wait()
		cv.notify()
		cv.release()
		
		print('Producer return run')
			

if __name__ == '__main__':

	c = Consumer(1)
	c.setDaemon(True)
	
	p = Producer(1)
	p.setDaemon(True)	
	
	c.start()
	p.start()
	
	c.join()
	p.join()
	
print('Exiting')
