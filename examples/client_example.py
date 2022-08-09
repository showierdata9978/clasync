
from clasync import Client
from asyncio import run

c = Client()

async def on_packet(packet):
    c.sendPacket(packet)

async def on_connect():
    c.sendPacket({"e":'e'})

c.callback(on_connect)
c.callback(on_packet)

run(c.run())