import asyncio
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.server import start_server

async def send(w,obj):
    w.write((json.dumps(obj)+'\n').encode());await w.drain()
async def receive(r,t):
    for _ in range(10):
        b=await asyncio.wait_for(r.readline(),1)
        if not b:raise AssertionError('Unexpected disconnect waiting for '+t)
        x=json.loads(b)
        if x.get('type')==t:return x
    raise AssertionError('Missing '+t)

class SoloBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.server=await start_server('127.0.0.1',0,'test-secret')
        self.port=self.server.sockets[0].getsockname()[1]
        self.connections=[]
    async def asyncTearDown(self):
        for _,w in self.connections:
            w.close();await w.wait_closed()
        self.server.close();await self.server.wait_closed()
    async def connect(self,role,player=None,secret='test-secret',expected='welcome'):
        r,w=await asyncio.open_connection('127.0.0.1',self.port)
        self.connections.append((r,w))
        await send(w,{'type':'hello','role':role,'player':player,'secret':secret})
        return r,w,await receive(r,expected)
    async def test_solo_event_adapter_and_self_cast(self):
        r,w,_=await self.connect('player','solo')
        ra,wa,_=await self.connect('adapter')
        await send(w,{'type':'event','payload':{'event_id':'fake','event':'mwiii_kill','player':'solo'}})
        self.assertIn('permission',(await receive(r,'error'))['message'])
        for i in range(4):
            await send(wa,{'type':'event','payload':{'event_id':f'kill-{i}','event':'mwiii_kill','player':'solo','victim':'enemy'}})
            await receive(r,'score');await receive(r,'state')
            await receive(ra,'score');await receive(ra,'state')
        await send(w,{'type':'cast','powerup':'cruise_missile'})
        x=await receive(r,'powerup')
        self.assertEqual(x['target'],'solo')
        self.assertEqual(x['points_remaining'],0)
    async def test_second_player_rejected(self):
        await self.connect('player','solo')
        _,_,result=await self.connect('player','bravo',expected='error')
        self.assertIn('solo session',result['message'])
    async def test_invalid_secret_rejected(self):
        _,_,reply=await self.connect('adapter',secret='wrong',expected='error')
        self.assertEqual(reply['message'],'authentication failed')

if __name__=='__main__':unittest.main()
