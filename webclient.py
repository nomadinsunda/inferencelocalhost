import json
import threading
import time
import pprint
import random
import asyncio
import stomper
import socket
import websockets
       
        
class WSClient:
    recv_timeout = 5
    ping_timeout = 5
    connection_failure_retry_sleep_time = 5
    stomp_connect_accept_packet = 'CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n'
        
    def __init__(self, connection_uri, subscribe_uri):
        self.connection_uri = connection_uri
        self.stomp_subscribe_uri = subscribe_uri
        self.retry_connection_counts = 0       
		    
    # To use asyncio, create a native coroutine with async def like this:
    # Create native coroutines with async def.
    async def listen_forever(self, cv, buffer):
        self.cv = cv
        self.buffer = buffer
        
        #await can only be used inside a native coroutine.
        
        while True:
        # outer loop restarted every time the connection fails
            try:
                async with websockets.connect(self.connection_uri) as ws:
                    print("connected with server")
                    await ws.send(WSClient.stomp_connect_accept_packet)
                    client_id = str(random.randint(0, 1000))
                    sub = stomper.subscribe(self.stomp_subscribe_uri, client_id, ack='auto')
                    await ws.send(sub)
                    reply = await asyncio.wait_for(ws.recv(), timeout=5)
                    
                    print(reply)

                    #await asyncio.sleep(5)           
                    
                    while True:
                    # listener loop
                        try: 
                            response = await asyncio.wait_for(ws.recv(), timeout=WSClient.recv_timeout)
                            
                            self.cv.acquire()
                            self.buffer.append(response)#self.buffer.append(msgtojson)
                            self.cv.notify()
                            self.cv.release()
                            #print('Result: {}'.format(reponse))
                            
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                            try:
                                pong = await ws.ping()
                                await asyncio.wait_for(pong, timeout=WSClient.ping_timeout)
                                print("Ping OK, keeping connection alive...")
                                #logger.debug('Ping OK, keeping connection alive...')
                                continue
                            except:
                                await asyncio.sleep(5)
                                print("Ping failure, keeping connection alive...")
                                break  # inner loop
                        # do stuff with reply object
            except socket.gaierror:
                print("socket.gaierror")
                # log something
                continue
            except ConnectionRefusedError:
                print("ConnectionRefusedError")
                await asyncio.sleep(WSClient.connection_failure_retry_sleep_time)
                # log something else
                continue
                
               
if __name__ == '__main__':
    wcs = WSClient()
    
    #wcs.connect_server2()
    #res = wcs.start_connect_server()
    asyncio.get_event_loop().run_until_complete(wcs.listen_forever())
    print("*******************************************")
    print("return run_until complete")
    print("*******************************************")
    #print(res)
    
    #res = wcs.start_com_server()
	#asyncio.get_event_loop().run_forever()
	#print("*******************************************")
	#print("return run_forever")
	#print("*********************************************")
