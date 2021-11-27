from peer import Peer
import asyncio

class PeerManager(object):
    def __init__(self, handshake_message, peer_list = []):
        self.peers = [Peer(peer[0], peer[1]) for peer in peer_list]
        self.avaible_peers = asyncio.Queue()
        self.handshake_message = handshake_message
        self.find_seeders()
        
    def add_peer(self, peer):
        self.peers.append(peer)
    
    def find_seeders(self):
        for peer in self.peers:
            data = asyncio.run(peer.send_message(self.handshake_message))
            if data:
                print("data -> ", data)
                
    def send_interested(self):
        for peer in self.peers:
            data = asyncio.run(peer.send_message(Message.Interested().encode()))
            print("data -> ", data)
        


