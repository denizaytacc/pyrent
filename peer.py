import asyncio
from send_message import send_message
from struct import unpack
from message import Message
class PeerManager(object):
    def __init__(self, handshake_message, peer_list = []):
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
            r2 = parse_handshake(data)
            if data:
                self.peer_status.append({"ip": peer[0], "port": peer[1], "bitfield": r2})
        print(self.peer_status)

    def send_interested(self):
        for peer in self.peer_status:
            data = asyncio.run(send_message(peer["ip"], peer["port"], Message.Interested()))
            print("data -> ", data)

def parse_handshake(data):
    if data:
        received_handshake = data[:68]
        seeder_status = False
        if len(received_handshake) == 68 and b'BitTorrent protocol' in received_handshake:
            r2 = None
            print("Handshake confirmed!")
            handshake = data[:68]
            if len(data) > 68:
                message = data[68:]
                print("Message len", len(message))
                payload_length, message_id = unpack(">IB", message[:5])
                print("Payload length", payload_length, "message_id", message_id)

                if message_id == 5:
                    bitfield_length = payload_length - 1
                    print("This is a bitfield message and the length of it is", bitfield_length)
                    try:
                        raw_bitfield, = unpack(">{}s".format(bitfield_length), message[5:5 + bitfield_length])
                        r2 = bin(int.from_bytes(raw_bitfield, byteorder="big")).strip('0b')
                        print(raw_bitfield)
                        print(r2)
                        print(len(r2))
                    except:
                        print("The client send incomplete bit field message")
                        raw_bitfield, = unpack(">{}s".format(len(message) - 5), message[5:])
                        r2 = bin(int.from_bytes(raw_bitfield, byteorder="big")).strip('0b')
                        print(raw_bitfield)
                        print(r2)
                        print(len(r2))
            return r2
    else:
        print("Handshake not confirmed")
