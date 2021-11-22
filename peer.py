import asyncio
from send_message import send_message
from struct import unpack
from message import Message, MessageParser
class PeerManager(object):
    def __init__(self, handshake_message, peer_list = []):
        self.message_parser = MessageParser()
        self.peers = peer_list
        self.peer_status = []
        self.handshake_message = handshake_message
        self.find_seeders()
        self.send_interested()
        
    def add_peer(self, peer):
        self.peers.append(peer)
    
    def find_seeders(self):
        for peer in self.peers:
            data = asyncio.run(send_message(peer[0], peer[1], self.handshake_message))
            print("data -> ", data)
            r2 = self.parse_handshake(data)
            if data:
                self.peer_status.append({"ip": peer[0], "port": peer[1], "bitfield": r2})
        print(self.peer_status)

    def send_interested(self):
        for peer in self.peer_status:
            data = asyncio.run(send_message(peer["ip"], peer["port"], Message.Interested()))
            print("data -> ", data)

    def parse_handshake(self, data):
        if data:
            received_handshake = data[:68]
            seeder_status = False
            if len(received_handshake) == 68 and b'BitTorrent protocol' in received_handshake:
                r2 = None
                print("Handshake confirmed!")
                handshake = data[:68]
                if len(data) > 68:
                    bitfield = self.message_parser.parse_bitfield(data[68:])
                    return bitfield
        else:
            print("Handshake not confirmed")
