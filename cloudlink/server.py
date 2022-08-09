import asyncio
import json

import websockets

version = "Async 0.0.0"

class server:
    
    def __init__(self, ip="127.0.0.1", port=3000,  debug=False) -> None:
        self.host = (ip, port)
        self.debug = debug
        self.callbacks = {
            "on_packet": [],
            "on_error": [],
            "on_connect": []
        }
        
        
        self.statedata = {
            "ulist": {
                "usernames": {},
                "objs": {}
            }, # Username list for the "Usernames" block
            "secure_enable": False, # Trusted Access enabler
            "secure_keys": [], # Trusted Access keys
            "gmsg": "", # Global data stream
            "motd_enable": False, # MOTD enabler
            "motd": self.statedata["motd"], # MOTD text
            "secure_enable": False, # Trusted Access enabler
            "secure_keys": [], # Trusted Access keys
            "trusted": [], # Clients that are trusted with Secure Access, references memory objects only
            "ip_blocklist": [] # Blocks clients with certain IP addresses
        }
        
    async def run(self):
        async with websockets.serve(self._ws_handle, self.host[0], self.host[1]):
            await asyncio.Future()
    
    
    async def _ws_handle(self, wss):
        self.statedata["ulist"]["objs"][str(wss.remote_address)] = {"wss":wss, "uname":"", "type": None, "ip": wss.remote_address}
        
        if self.statedata["motd_enable"]:
            await wss.send(json.dumps({"cmd": "direct", "val": {"cmd": "motd", "val": str(self.statedata["motd"])}}))

        await wss.send(json.dumps({"cmd": "direct", "val": {"cmd": "vers", "val": str(version)}}))
        
        if not self.statedata["secure_enable"]:
            # Send the current username list.
            await wss.send(json.dumps({"cmd": "ulist", "val": self._get_ulist()}))
            # Send the current global data stream value.
        
            await wss.send(json.dumps({"cmd": "gmsg", "val": str(self.statedata["gmsg"])}))
        else:
            # Tell the client that the server is expecting a Trusted Access key. 
            await wss.send(json.dumps({"cmd": "statuscode", "val": self.codes["TAEnabled"]}))

        try:
            async for callback in self.callbacks["on_connect"]:
                await callback(wss) #client
        except KeyError:
            pass

        while True:
            await asyncio.sleep(0)
            async for msg in wss:
                packet = json.loads(msg)
                try:
                    async for callback in self.callbacks["on_connect"]:
                        await callback(wss, packet) #client
                except KeyError:
                    pass
            
    async def SendPacket(self, user, packet):
        if type(user) == str:
            self.statedata["ulist"]["usernames"][user]["wss"].send(json.dumps(packet))
        else:
            user.send(json.dumps(packet))