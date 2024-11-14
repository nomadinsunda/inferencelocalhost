##! /usr/bin/python

import threading #To create a thread in Python, you can use the threading module (high level) or the thread module (low level). 
				 #In general, for thread processing, the threading module implemented on top of the thread module is used, and the thread module is rarely used (deprecated).
import signal
import time
import sys
import os
import json
import random
import irreq
import numpy as np

import base64
import stomp_msg
import io
import tensorflow as tf
from tensorflow import keras
from PIL import Image

exitto = False

class Consumer(threading.Thread):	# threading.Thread is super class
    def __init__(self, threadID, jwtoken, inspection_result_url, inspection, cv, buffer):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.auth_token = jwtoken
        self.inspection_result_url = inspection_result_url
        self.inspection = inspection
        self.cv = cv
        self.buffer = buffer
        
    def getSTOMPMessage(self, response):
        msg = stomp_msg.StompMSG(response)
                
        realmsg = msg.getstompmessage()
        msgtojson = json.loads(realmsg)
        content = msgtojson['content']
             
        decodingstobytearray = base64.b64decode(content)
        stream = io.BytesIO(decodingstobytearray)
        img = Image.open(stream)
        
        filenamekey = msgtojson['key']
        print('filename:', filenamekey)
        splitstrs = filenamekey.split('/')
        print(len(splitstrs))
        pngextend = '.png'
        for string in splitstrs:#for string in enumerate(splitstrs):
            if string.find(pngextend) != -1:
                pngfilename = string
                bmpfilename = string.split('.')[0] + '.bmp'
                break
            
        print('png filename:', pngfilename)
        print('bmp filename:', bmpfilename)
        img.save(pngfilename)
        Image.open(pngfilename).save(bmpfilename)
        
        return bmpfilename, filenamekey
        
        
		
    def processing_result(self, filenamekey, results):
        
        num_det_ob = results.get('num_det_ob')
        if num_det_ob == 1:
            rect_sample = results.get('rect_samples')[0]
            score = results.get('scores')[0]
            predcl = results.get('predcls') 
            print('rect_sample=', rect_sample)
            print('score=', score)
            print('predcl=', predcl)
            
            print('rect_sample[0]=', rect_sample[0]) #ymin
            print('rect_sample[1]=', rect_sample[1]) #xmin
            print('rect_sample[2]=', rect_sample[2]) #ymax
            print('rect_sample[3]=', rect_sample[3]) #xmax
                                
            result_json_object = {
                "type": "INFERENCE",
                "key": "admin@vazilcompany.com/바질컴퍼니/CAP-0001/5d529bbcf8fe714code1c402a.png",
                "content": {
                    "ymin": 0,
                    "xmin": 0,
                    "ymax": 0,
                    "xmax": 0,
                    "score": 0,
                    "classification": "NG"
                    },
                 "sender": "inference agent"
            }            
            
            #result_json_object['key'] = 'helloworld.bmp'
            result_json_object['key'] = filenamekey.__str__()
            
            result_json_object['content']['ymin'] = rect_sample[0]
            result_json_object['content']['xmin'] = rect_sample[1]
            result_json_object['content']['ymax'] = rect_sample[2]
            result_json_object['content']['xmax'] = rect_sample[3]
            result_json_object['content']['score'] = score
            
            if predcl == 1:
                result_json_object['content']['classification'] = "G"                
                
            strx = result_json_object['content']
            result_json_object['content'] = strx.__str__()
            
            irreq.postInferenceResult(self.auth_token, self.inspection_result_url, result_json_object)
                        
            print("result_json_string=", result_json_object)
        
    def run(self):
                
		#print('******************************************************')
        print(f'Consumer thread[{self.threadID}] is run')
		#print('******************************************************')
		#for x in range(5):
        continuex = True
        while continuex :#len(buffer) < 1:
            self.cv.acquire()
			
            print('******************************************************')
            if not self.buffer and exitto == False: #if not buffer:
                print(f'Consumer thread[{self.threadID}] waiting...')
                self.cv.wait()
			
            if exitto:
                continuex = False
                print('Consumer is exit...')
				#print('******************************************************')
                self.cv.release()
                break				
            else:
                if self.buffer:
                    gotItem = self.buffer.pop(0)
                    self.cv.release()
                    bmpfilename, filenamekey = self.getSTOMPMessage(gotItem)
                    
                    
                    #results = self.inspection.start_processing1()
                    results = self.inspection.start_processing(bmpfilename)
                    self.processing_result(filenamekey, results)
                    
                else :
                    self.cv.release()
                    print('Consumer buffer is empty')
					
                print('******************************************************')
                #self.cv.release()
				
			#time.sleep(0.01)
			
        print('Consumer return run')

if __name__ == '__main__':

	c = Consumer(1)
	c.setDaemon(True)    
	
	
print('Exiting')
