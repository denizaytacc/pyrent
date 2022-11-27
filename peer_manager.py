from peer import Peer
import asyncio
from collections import deque
from message import Message

class PeerManager(object):
    def __init__(self, handshake_message, pieces_hash, peer_list):
        self.block_size = 2 ** 14
        self.peers = [Peer(peer[0], peer[1]) for peer in peer_list]
        self.handshake_message = handshake_message
        self.pieces_hash = pieces_hash
        self.downloaded_pieces = [0 for _ in range(len(pieces_hash) // 20)]
        # needed for synchronously running stuff
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect_seeders())
        self.loop.run_until_complete(self.send_interested())

    # tries to connect peers if they already not handshaken with
    async def connect_seeders(self):
        q = deque(self.peers)
        tasks = list()
        while len(q) > 0:
            peer = q.pop()
            if peer.handshaken == False:
                task = asyncio.create_task(peer.send_handshake(self.handshake_message))
                tasks.append(task)
        await asyncio.gather(*tasks)

    # send interested message for handshaken users   
    async def send_interested(self):
        msg = Message.Interested()
        q = deque([peer for peer in self.peers if peer.handshaken == True])
        tasks = list()
        while len(q) > 0:
            peer = q.pop()
            task = asyncio.create_task(peer.send_message(msg))
            tasks.append(task)
        await asyncio.gather(*tasks)


