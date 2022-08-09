import asyncio
import json

import websockets

class Client:
    def __init__(self, server="127.0.0.1:3000", debug=False) -> None:
        self.server = server
        self.debug = debug
        self.callbacks = {}
 
        self.statedata = {
            "ulist": {
                "usernames": []
            },
        }   
    
    async def run(self):
        """Runs the client"""
        try:
            async with websockets.connect(self.server) as ws:
                
                self._ws = ws
                try:
                    try:
                        async for callback in self.callbacks["on_connect"]:
                            await callback(packet)
                    except KeyError:
                        pass
                    
                    while True: # main loop
                        async for message in ws:
                            packet:dict = json.loads(message)
                            if (("cmd" in packet) and (packet["cmd"] == "ulist")) and ("val" in packet):
                                self.statedata["ulist"]["usernames"] = str(packet["val"]).split(";")
                            
                            try:
                                async for callback in self.callbacks["on_packet"]:
                                    await callback(packet)
                            except KeyError:
                                pass
                except websockets.ConnectionClosedOK:
                    try:
                        async for callback in self.callbacks["on_close"]:
                            await callback(True) #arg is OK
                    except KeyError:
                        pass
                except websockets.ConnectionClosedError:
                    try:
                        async for callback in self.callbacks["on_close"]:
                            await callback(False) #arg is OK
                    except KeyError:
                        pass
                    
        except Exception as e:
            try:
                async for callback in self.callbacks["on_error"]:
                    await callback(e)
            except KeyError: 
                pass
            
            except Exception as e:
                if self.debug:
                    print(f"Error in a on_error callback ({e})") 

    def callback(self, cb, callback_id:str = None):
        """adds a callback to clasync

        Args:
            cb (function): the callback
            callback_id (str, optional): what the callback is supost to be for. Defaults to None.
        """
        try:
            self.callbacks[callback_id or cb.__name__].append(cb)
        except KeyError:
            self.callbacks[callback_id or cb.__name__] = [cb]
    
    async def stop(self):
        """stops the ws client
        """
        await self._ws.wait_closed()
        try:
            async for callback in self.callbacks["on_close"]:
                await callback(True) #arg is OK
        except KeyError:
            pass
                    
                    
    async def sendPacket(self, packet):
        """Sends a packet to the server

        Args:
            packet (Any): the packet you want to send
        """
        
        pckt = json.dumps(packet)
        await self._ws.send(pckt)