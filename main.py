import time
import asyncio
import irreq
import threading
import consumer
import webclient
#import inference
import inference_class as ic
import asyncio

asyncio.apply() #for anaconda env...remove under linux!!!

login_url = 'http://x.x.x.x:8080/api/auth/login'
websocket_connection_uri = 'ws://x.x.x.x:5000/ws'
inspection_result_url = 'http://x.x.x.x:x/api/inference/result'


username = 'admin@example.com'
password = '1234'

stomp_subscribe_uri = '/topic/ai.inference.result'

buffer = [] # Define Empty List
cvi = threading.Condition()

if __name__ == '__main__':
    print('name=', __name__)

    inspection = ic.DefectInspection("./project_dir/models")
    inspection.load_models()
    
    jwtoken = irreq.loginWebserver(login_url, username, password)
    #time.sleep(5)
    
    consumer = consumer.Consumer(0, jwtoken, inspection_result_url, inspection, cvi, buffer)
    consumer.start()    
    
    wcs = webclient.WSClient(websocket_connection_uri, stomp_subscribe_uri)
    
    # change thread!!!
    # need while loop
    # The event loop is the heart of any asyncio application. 
    # The event loop executes asynchronous tasks and callbacks, performs network IO operations, and executes child processes.
    asyncio.get_event_loop().run_until_complete(wcs.listen_forever(cvi, buffer))
    
