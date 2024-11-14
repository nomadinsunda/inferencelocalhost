import json
import pprint
import random
import asyncio
import stomper
import socket
import websockets
	
class WSClient:
    #uri = "ws://localhost:8765"
    connection_uri = "ws://133.186.162.169:5000/ws"
    subscribe_uri = '/topic/ai.inference.result'
    ping_timeout = 5
    connection_failure_retry_sleep_time = 5
    #g_websocket = 0
    
    def __init__(self):
        self.retry_connection_counts = 0
        
    async def connect_server(self):
        self.retry_connection_counts = 12
        
        for i in range(0, self.retry_connection_counts):
        #while self.retry_connection_counts > 0:
        # outer loop restarted every time the connection fails
            #self.retry_connection_counts-- 
            try:
                async with websockets.connect(WSClient.connection_uri) as self.websocket:
                    #self.websocket = ws
                    #WSClient.g_websocket = ws
                    print("connected with server")
                    try:
                        await self.websocket.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")
                        self.client_id = str(random.randint(0, 1000))
                        sub = stomper.subscribe(WSClient.subscribe_uri, self.client_id, ack='auto')
                        await self.websocket.send(sub)
                        reply_connected = await asyncio.wait_for(self.websocket.recv(), timeout=5)
                        #print('Result: {}'.format(reply_connected))
                        print(reply_connected)
                        return reply_connected
                    except (asyncio.TimeoutError, websockets.exception.ConnectionClosed):
                        try:
                            pong = await self.websocket.ping()
                            await asyncio.wait_for(pong, WSClient.ping_timeout)
                            print('Ping Ok, keeping connection alive...')
                            
                        except:
                            print('why???...')
                            #break
                            
            except socket.gaierror:
                print("socket.gaierror")
                # log something
                continue
            except ConnectionRefusedError:
                print("ConnectionRefusedError")
                await asyncio.sleep(WSClient.connection_failure_retry_sleep_time)
                # log something else
                continue
                
                
    def connect_server2(self):
        self.retry_connection_counts = 12
        
        for i in range(0, self.retry_connection_counts):
        #while self.retry_connection_counts > 0:
        # outer loop restarted every time the connection fails
            #self.retry_connection_counts-- 
            
                self.websocket = websockets.connect(WSClient.connection_uri)
                #self.websocket = ws
                #WSClient.g_websocket = ws
                print("connected with server")
                
                    self.websocket.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")
                    self.client_id = str(random.randint(0, 1000))
                    sub = stomper.subscribe(WSClient.subscribe_uri, self.client_id, ack='auto')
                    self.websocket.send(sub)
                    reply_connected = asyncio.wait_for(self.websocket.recv(), timeout=5)
                    #print('Result: {}'.format(reply_connected))
                    print(reply_connected)
                    return reply_connected
                 (asyncio.TimeoutError, websockets.exception.ConnectionClosed):
                    try:
                        pong = self.websocket.ping()
                        asyncio.wait_for(pong, WSClient.ping_timeout)
                        print('Ping Ok, keeping connection alive...')
                        
                    except:
                        print('why???...')
                        #break
                            
            except socket.gaierror:
                print("socket.gaierror")
                # log something
                continue
            except ConnectionRefusedError:
                print("ConnectionRefusedError")
                asyncio.sleep(WSClient.connection_failure_retry_sleep_time)
                # log something else
                continue
                
    def start_connect_server(self):
        return asyncio.get_event_loop().run_until_complete(self.connect_server())
                
                
                
    async def recv_forever(self):                                
        while True:
        # listener loop
            try:
                
                print("set data")
                #senddata = json.load('{"type":"INTERFACE", "key":"testfile.txt", "content":"ok", "sender":"API Server"}')#json.dumps({"hello world"})
                #name = "swseo"
                send_message = stomper.send("/app/ai.inference.result", json.dumps([json.dumps({"type":"INTERFACE", "key":"testfile.txt", "content":"ok", "sender":"API Server"})]))

                #await self.websocket.send(send_message)
                await self.websocket.send(send_message)
                print('send send message')
                
                reply = await asyncio.wait_for(self.websocket.recv(), timeout=5)
                #print(f"< {reply}")
                print('Result: {}'.format(reply))
                
                await asyncio.sleep(5)
                
            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                try:
                    pong = await self.websocket.ping()
                    await asyncio.wait_for(pong, timeout=5)
                    print("Ping OK, keeping connection alive...")
                    #logger.debug('Ping OK, keeping connection alive...')
                    continue
                except:
                    print("Ping Failure...")
                    await asyncio.sleep(5)
                    break  # inner loop
                # do stuff with reply object
            except socket.gaierror:
                print("socket.gaierror")
                # log something
                continue
            except ConnectionRefusedError:
                print("ConnectionRefusedError")
                await asyncio.sleep(1)
                # log something else
                continue
                
    def start_com_server(self):
        return asyncio.get_event_loop().run_until_complete(self.recv_forever())
                
    async def listen_forever(self):
        while True:
        # outer loop restarted every time the connection fails
            try:
                async with websockets.connect(WSClient.connection_uri) as ws:
                    print("connected with server")
                    await ws.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")
                    client_id = str(random.randint(0, 1000))
                    sub = stomper.subscribe("/topic/ai.inference.result", client_id, ack='auto')
                    await ws.send(sub)
                    reply = await asyncio.wait_for(ws.recv(), timeout=5)
                    #print(f"< {reply}")
                    print('Result: {}'.format(reply))                   
                    
                    
                    while True:
                    # listener loop
                        try:
                            await asyncio.sleep(5)
                            print("set data")
                            #senddata = json.load('{"type":"INTERFACE", "key":"testfile.txt", "content":"ok", "sender":"API Server"}')#json.dumps({"hello world"})
                            #name = "swseo"

                            send_message = stomper.send("/app/ai.inference.result", json.dumps([json.dumps({"type":"INTERFACE", "key":"testfile.txt", "content":"ok", "sender":"API Server"})]))
        
                            await ws.send(send_message)                            
                            
                            reply = await asyncio.wait_for(ws.recv(), timeout=5)
                            #print(f"< {reply}")
                            print('Result: {}'.format(reply))
                            
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                            try:
                                pong = await ws.ping()
                                await asyncio.wait_for(pong, timeout=5)
                                print("Ping OK, keeping connection alive...")
                                #logger.debug('Ping OK, keeping connection alive...')
                                continue
                            except:
                                await asyncio.sleep(5)
                                break  # inner loop
                        # do stuff with reply object
            except socket.gaierror:
                print("socket.gaierror")
                # log something
                continue
            except ConnectionRefusedError:
                print("ConnectionRefusedError")
                await asyncio.sleep(1)
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
    print(res)
    
    res = wcs.start_com_server()
	#asyncio.get_event_loop().run_forever()
	#print("*******************************************")
	#print("return run_forever")
	#print("*********************************************")
