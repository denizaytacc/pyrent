import asyncio
from struct import unpack
from message import Message, MessageParser
import socket
import logging

# Is this will work?

logging.basicConfig(
    filename = "torrent_log.log",
    level = logging.DEBUG,
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b-%y %H:%M:%S',
)


class Peer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.writer = None
        self.reader = None
        self.choked = True
        self.interested = False
        self.connected = False
        self.pieces = {}
        self.loop = asyncio.get_event_loop()

    async def send_message(self, message):
        if self.reader == None:
            try:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.ip, self.port), 3)
                logging.info(f"Successfully connected to {self.ip}:{self.port}")
                self.connected = True
            except:
                logging.error(f"Error while connecting to the {self.ip}:{self.port}")
                
        if self.connected == True:
            try:
                print(f"send {message} to {self.ip} {self.port}")
                self.writer.write(message)
                await self.writer.drain()
                buffer = b''
                buffer = await self.reader.read(4096)
                tries = 1
                while len(buffer) < 68 and tries < 10:
                    tries += 1
                    buffer = await self.reader.read(4096)
                print(buffer)
                self.parse_handshake(buffer)

            except Exception as e:
                print(e)

    async def close(self):
        logging.info(f"Closed the connection with {self.ip} {self.port}")
        print('Closed the connection')
        self.writer.close()
        await writer.wait_closed()
        
    def parse_handshake(self, data):
        if data:
            received_handshake = data[:68]
            seeder_status = False
            if len(received_handshake) == 68 and b'BitTorrent protocol' in received_handshake:
                r2 = None
                print("Handshake confirmed!")
                handshake = data[:68]
                if len(data) > 68:
                    bitfield = MessageParser.parse_bitfield(data[68:])
                    self.pieces = bitfield
        else:
            print("Handshake not confirmed")
