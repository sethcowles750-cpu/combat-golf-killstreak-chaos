import asyncio
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.server import start_server

async def request(writer, payload):
    writer.write((json.dumps(payload)+'\n').encode());await writer.drain()
async def read_until(reader, expected):
    for _ in range(10):
        obj=json.loads(await asyncio.wait_for(reader.readline(),1))
        if obj.get('type')==expected:return obj
    raise AssertionError('No '+expected+' received')

class RelayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.server=await start_server('127.0.0.1',0,'local-secret')
        self.port=self.server.sockets[0].getsockname()[1]
        self.pairs=[]
    async def asyncTearDown(self):
        for _,w in self.pairs: w.close();await w.wait_closed()
        self.server.close();await self.server.wait_closed()
    async def connect(self,role,player=None,secret='local-secret'):
        r,w=await asyncio.open_connection('127.0.0.1',self.port)
        self.pairs.append((r,w))
        await request(w,{'type':'hello','role':role,'player':player,'secret':secret})
        obj=await read_until(r,'welcome' if secret=='local-secret' else 'error')
        return r,w,obj
    async def test_two_players_get_same_killstream_and_cast(self):
        a,aw,_=await self.connect('player','alpha')
        b,bw,_=await self.connect('player','bravo')
        r,rw,_=await self.connect('adapter')
        await request(aw,{'type':'event','payload':{'event_id':'fake','event':'mwiii_kill','player':'alpha'}})
        denied=await read_until(a,'error')
        self.assertIn('permission',denied['message'])
        for i in range(4):
            await request(rw,{'type':'event','payload':{'event_id':f'k{i}', 'event':'mwiii_kill','player':'alpha','victim':'enemy'}})
            await read_until(a,'score');await read_until(a,'state')
            await read_until(b,'score');await read_until(b,'state')
        await request(aw,{'type':'cast','powerup':'cruise_missile','target':'bravo'})
        x=await read_until(a,'powerup')
        y=await read_until(b,'powerup')
        self.assertEqual(x['sequence'],y['sequence'])
        self.assertEqual(x['effect'],'impulse')
        self.assertEqual(x['points_remaining'],0)
    async def test_wrong_secret_rejected(self):
        r,w,response=await self.connect('adapter',secret='wrong')
        self.assertEqual(response['message'],'authentication failed')

if __name__=='__main__':unittest.main()
