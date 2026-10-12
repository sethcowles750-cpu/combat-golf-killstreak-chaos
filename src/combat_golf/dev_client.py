"""Manual developer event client. Inputs here are simulated, not live game data."""
import argparse
import asyncio
import json
import os


async def main_async(args):
    reader, writer = await asyncio.open_connection('127.0.0.1', args.port)
    async def send(item):
        writer.write((json.dumps(item) + '\n').encode()); await writer.drain()
    await send({'type':'hello','role':args.role,'player':args.player,'secret':args.secret})
    async def receive():
        while (line := await reader.readline()):
            print('FROM HOST', line.decode().strip(), flush=True)
    task = asyncio.create_task(receive())
    print('DEV SIMULATION ONLY: commands: kill PLAYER, hole PLAYER HOLE_ID STROKES PAR, cast POWER [TARGET], state, quit')
    counter = 0
    try:
        while True:
            command = await asyncio.to_thread(input, '> ')
            parts = command.split()
            if not parts: continue
            if parts[0] == 'quit': break
            counter += 1
            if parts[0] == 'kill' and len(parts) == 2 and args.role == 'adapter':
                req = {'type':'event', 'payload':{'event_id':f'devkill-{counter}', 'event':'mwiii_kill','player':parts[1]}}
            elif parts[0] == 'hole' and len(parts) == 5 and args.role == 'adapter':
                req = {'type':'event', 'payload':{'event_id':f'devhole-{counter}', 'event':'golf_hole_completed','player':parts[1], 'hole_id':parts[2], 'strokes':int(parts[3]), 'par':int(parts[4])}}
            elif parts[0] == 'cast' and len(parts) in (2,3) and args.role == 'player':
                req = {'type':'cast', 'powerup':parts[1], 'target':parts[2] if len(parts) == 3 else None}
            elif parts[0] == 'state': req = {'type':'state'}
            else:
                print('Invalid command or role'); continue
            await send(req)
    finally:
        writer.close(); await writer.wait_closed()
        task.cancel()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--role', choices=('adapter','player'),required=True)
    parser.add_argument('--player',default=None)
    parser.add_argument('--secret',default=os.getenv('COMBAT_GOLF_DEV_SECRET'))
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if not args.secret: parser.error('set COMBAT_GOLF_DEV_SECRET or --secret to local server secret')
    asyncio.run(main_async(args))

if __name__=='__main__':main()
