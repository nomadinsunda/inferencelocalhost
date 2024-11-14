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
from PIL import Image

exitto = False

class Consumer(threading.Thread):	# threading.Thread is super class
    def __init__(self, threadID, jwtoken, inspection, cv, buffer):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.auth_token = jwtoken
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
        #img.getdata()
        #data = [img.getpixel((x, y)) for x in range(img.width) for y in range(img.height)]
        #print(data)
        filename = msgtojson['key']
        print('filename:', filename)
        splitstrs = filename.split('/')
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
        
        #filename = '/5d529bb6f8fe714cde1c401e.png'
        #img.save(filename)
        #Image.open(filename).save("sample2.bmp")
        
        
        #pre_img = decodingstobytearray.hex()
        #print(decodingstobytearray.hex())
        #im = Image.frombuffer('L', (800, 600), decodingstobytearray, 'raw', 'L', 0, 1)
        #im = Image.frombytes('L', (800,600), decodingstobytearray, 'raw', 'L', 0, 1)
        #im = Image.frombytes('RGB', (800,600), decodingstobytearray, 'raw')
        #im.save('result.png')                            
        
        #img = Image.fromarray(decodingstobytearray, 'RGB')
        #img.save('my.png') 
                  
        
        #print(decodingstobytearray)
        #print(f"< {reponse}")
        #
        # here!!!
        # we push that at queue!!!--->producer
        #
		
    def processing_result(self, results):
        
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
        
            data = {'type':'INFERENCE',
                    'key':'helloworld.bmp',
                    'content':"{\'ymin\':200,\'xmin\':50,\'ymax\':150,\'xmax\':200,\'score\':87.2,\'classification\':\'OK\'}",#'content':'OK',
                    'sender':'inference agent'}
        
            #real_data = {}
            #real_data['type'] = 'INFERENCE'
            #real_data['key'] = 'helloworld.bmp'
            #real_data.setdefault('content', np.zeros((num_det_ob, 4), float))
            #real_data['content']['ymin'] = rect_sample[0]
            #real_data['content']['xmin'] = rect_sample[1]
            #real_data['content']['ymax'] = rect_sample[2]
            #real_data['content']['xmax'] = rect_sample[3]
            #real_data['content']['score'] = score
            #real_data['content']['classification'] = 1
            #real_data['sender'] = 'inference agent'
            #print("real_data=", real_data)        
        
            result_json_object = {
                "type": "INFERENCE",
                "key": "helloworld.bmp",
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
            
            #result_json_object['type'] = 'INFERENCE'
            result_json_object['key'] = 'helloworld.bmp'  #WE need file name!!!
            result_json_object['content']['ymin'] = rect_sample[0]
            result_json_object['content']['xmin'] = rect_sample[1]
            result_json_object['content']['ymax'] = rect_sample[2]
            result_json_object['content']['xmax'] = rect_sample[3]
            result_json_object['content']['score'] = score
            if predcl == 1:
                result_json_object['content']['classification'] = "G"
                
            strx = result_json_object['content']
            result_json_object['content'] = strx.__str__()
            #result_json_object['sender'] = 'inference agent'
            #result_json_object['content'] = "{\'x\':200,\'y\':50,\'width\':150,\'height\':200,\'score\':87.2,\'labelName\':\'OK\'}"
            #result_json_object['content'] = "{\"x\":200,\"y\":50,\"width\":150,\"height\":200,\"score\":87.2,\"labelName\":\"OK\"}"
            
        
            #result_json_string = json.dumps(result_json_object)            
            #irreq.postInferenceResult(self.auth_token, result_json_string)
            irreq.postInferenceResult(self.auth_token, result_json_object)
            
            print("result_json_string[content]=", result_json_object['content'])
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
                    bufferV = self.buffer.pop(0)
                    self.cv.release()
                    self.getSTOMPMessage(bufferV)
                    
                    results = self.inspection.start_processing1()
                    self.processing_result(results)
                    #result = self.inspection.start_processing2()
                    #print('Consumer result:', results)
                                        #we need to processing
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
        
	#pro = []

	#for i in range(NR_CONSUMER):
		#c = Consumer(i)
		#c.setDaemon(True)
		#con.append(c)
	
	#for i in range(NR_PRODUCER):
		#p = Producer(i)
		#pro.append(p)
		
	#for th in con:
		#th.start()
		
	#for th in pro:
		#th.start()
		
	#for th in con:
		#th.join()
		
	#for th in pro:
		#th.join()
	
print('Exiting')
