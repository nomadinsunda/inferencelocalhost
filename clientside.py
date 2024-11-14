import json
import pprint
import random
import asyncio
import stomper
import socket
import websockets
	
class WSClient:
    uri = "ws://localhost:8765"
    ping_timeout = 1
    sleep_time = 1
    
    async def listen_forever(self):
        while True:
        # outer loop restarted every time the connection fails
            try:
                async with websockets.connect("ws://192.168.1.49:5000/ws") as ws:
                    print("connected with server")
                    await ws.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")
                    client_id = str(random.randint(0, 1000))
                    sub = stomper.subscribe("/topic/ai.inference.result", client_id, ack='auto')
                    await ws.send(sub)
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
    asyncio.get_event_loop().run_until_complete(wcs.listen_forever())
    print("*******************************************")
    print("return run_until complete")
    print("*******************************************")
	#asyncio.get_event_loop().run_forever()
	#print("*******************************************")
	#print("return run_forever")
	#print("*********************************************")
