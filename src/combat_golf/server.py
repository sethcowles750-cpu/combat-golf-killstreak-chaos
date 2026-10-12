"""Single-player loopback development bridge. Not a game multiplayer service.

Only one player and one synthetic adapter can attach. This does not read MWIII
kills or move real golf balls. Do not present it as playable game integration.
"""
import argparse
import asyncio
import json
import os
import secrets
import sys
from typing import Any
from .engine import Match, GameRuleError

MAX_LINE_BYTES = 8192


class Relay:
    def __init__(self, secret: str):
        if not secret: raise ValueError('nonempty secret required')
        self.secret = secret
        self.match = Match()
        self.peers: dict[asyncio.StreamWriter, tuple[str, str | None]] = {}
        self.lock = asyncio.Lock()

    @staticmethod
    async def send(writer: asyncio.StreamWriter, data: dict):
        writer.write((json.dumps(data, separators=(',', ':'), ensure_ascii=True) + '\n').encode('utf-8'))
        await writer.drain()

    async def broadcast(self, data: dict):
        for writer in list(self.peers):
            try:
                await self.send(writer, data)
            except (ConnectionError, OSError):
                self.peers.pop(writer, None)

    async def serve_peer(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            line = await reader.readline()
            if not line or len(line) > MAX_LINE_BYTES:
                return
            hello = json.loads(line)
            if hello.get('type') != 'hello' or not secrets.compare_digest(str(hello.get('secret','')), self.secret):
                await self.send(writer, {'type':'error', 'message':'authentication failed'})
                return
            role = hello.get('role')
            name = hello.get('player') if role == 'player' else None
            if role not in ('adapter', 'player'):
                await self.send(writer, {'type':'error','message':'role must be adapter or player'})
                return
            async with self.lock:
                if role == 'player' and any(r=='player' for r,_ in self.peers.values()):
                    raise GameRuleError('solo session already has a connected player')
                if role == 'adapter' and any(r=='adapter' for r,_ in self.peers.values()):
                    raise GameRuleError('solo session already has an event adapter')
                if role == 'player': self.match.add_player(name)
                self.peers[writer] = (role, name)
                await self.send(writer, {'type':'welcome','role':role,'player':name,'state':self.match.state()})
            while True:
                line = await reader.readline()
                if not line: break
                if len(line) > MAX_LINE_BYTES:
                    await self.send(writer, {'type':'error', 'message':'message too long'})
                    break
                try:
                    req: dict[str, Any] = json.loads(line)
                    if not isinstance(req, dict): raise GameRuleError('expected JSON object')
                    async with self.lock:
                        kind = req.get('type')
                        if kind == 'state':
                            await self.send(writer, {'type':'state', 'state':self.match.state()})
                        elif kind == 'event' and role == 'adapter':
                            outcome = self.match.record_event(req.get('payload'))
                            await self.broadcast(outcome)
                            await self.broadcast({'type':'state','state':self.match.state()})
                        elif kind == 'cast' and role == 'player':
                            outcome = self.match.cast(name, req.get('powerup'), req.get('target'))
                            await self.broadcast(outcome)
                            await self.broadcast({'type':'state','state':self.match.state()})
                        else:
                            raise GameRuleError('permission denied or unknown action')
                except (GameRuleError, ValueError, TypeError, json.JSONDecodeError) as exc:
                    await self.send(writer, {'type':'error', 'message':str(exc)})
        except (ConnectionError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            try: await self.send(writer, {'type':'error','message':str(exc)})
            except (ConnectionError, OSError): pass
        finally:
            async with self.lock: self.peers.pop(writer, None)
            writer.close()
            try: await writer.wait_closed()
            except (ConnectionError, OSError): pass


async def start_server(host: str, port: int, secret: str):
    relay = Relay(secret)
    return await asyncio.start_server(relay.serve_peer, host=host, port=port, limit=MAX_LINE_BYTES)


async def run(args):
    secret = args.secret or os.getenv('COMBAT_GOLF_DEV_SECRET') or secrets.token_urlsafe(24)
    if args.host != '127.0.0.1':
        raise SystemExit('Development relay only supports 127.0.0.1; remote hosting not implemented')
    server = await start_server(args.host, args.port, secret)
    print('DEV ONLY: single-player local bridge. No real MWIII or golf hooks connected.', flush=True)
    print(f'Address: {args.host}:{server.sockets[0].getsockname()[1]}', flush=True)
    print(f'Dev secret (keep local; never commit): {secret}', flush=True)
    async with server: await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Local development event relay')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--secret', default=None, help='local-only dev shared secret')
    args = parser.parse_args()
    try: asyncio.run(run(args))
    except KeyboardInterrupt: print('stopped')


if __name__ == '__main__': main()
