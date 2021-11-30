from peer import Peer
import asyncio
from message import Message

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class PeerManager(object):
    def __init__(self, handshake_message, peer_list = []):
        self.peers = [Peer(peer[0], peer[1]) for peer in peer_list]
        self.handshake_message = handshake_message
        self.find_seeders()
        self.send_interested()
        
    def add_peer(self, peer):
        self.peers.append(peer)
    
    def find_seeders(self):
        for peer in self.peers:
            data = loop.run_until_complete(peer.send_handshake(self.handshake_message))
                
    def send_interested(self):
        msg = Message.Interested()
        for peer in self.peers:
            if peer.connected:
                data = loop.run_until_complete(peer.send_message(msg))
                if data:
                    print(peer.parse_message(data))
            


