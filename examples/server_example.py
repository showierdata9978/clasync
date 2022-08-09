from asyncio import run

from clasync import server

s = server()

async def on_packet(packet, client):
    s.sendPacket(client, packet)


run(s.start())