import asyncio
from struct import unpack
from message import Message
import socket
import logging


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
        self.handshaken = False
        self.pieces = {}

    async def close_connection(self):
        logging.info(f"Closed the connection with {self.ip} {self.port}")
        print('Closed the connection')
        self.writer.close()
        await writer.wait_closed()

    async def send_handshake(self, message):
        data = await self.send_message(message)
        if data:
            received_handshake = data[:68]
            seeder_status = False
            if len(received_handshake) == 68 and b'BitTorrent protocol' in received_handshake:
                r2 = None
                print("Handshake confirmed!")
                self.handshaken = True
                handshake = data[:68]
                if len(data) > 68:
                    bitfield = self.parse_message(data[68:])
                    self.pieces = bitfield

    async def send_message(self, message):
        if self.connected == False:
            try:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.ip, self.port), 1)
                logging.info(f"Successfully connected to {self.ip}:{self.port}")
                self.connected = True
            except:
                logging.error(f"Error while connecting to the {self.ip}:{self.port}")
        if self.connected:
            try:
                #print(f"send {message} to {self.ip} {self.port}")
                self.writer.write(message)
                await self.writer.drain()
                buffer = b''
                buffer = await self.reader.read(4096)
                tries = 1
                while len(buffer) < 68 and tries < 10:
                    tries += 1
                    buffer = await asyncio.wait_for(self.reader.read(4096), 10)
                #print(buffer)
                if b"BitTorrent protocol" not in message: # means it wasn't a handshake and should be parsed
                    self.parse_message(buffer)
                return buffer

            except Exception as e:
                print(e)

    def parse_message(self, message):
        print("received", message)
        message_length_ = int.from_bytes(message[:4], byteorder='big')
        id_ = int.from_bytes(message[4:5], byteorder='big')
        if id_ == 1:
            print("Client unchoked you!")
            self.choked = False

        if id_ == 5:
            print("Parsing bitfield")
            self.parse_bitfield(message)

        if(len(message) - message_length_ > 0):
            self.parse_message(message[4 + message_length_:])    

    def parse_bitfield(self, message):
        message_length_ = int.from_bytes(message[:4], byteorder='big')
        bitfield_length = message_length_ - 1
        try:
            raw_bitfield, = unpack(">{}s".format(bitfield_length), message[5:5 + bitfield_length])
            bitfield = bin(int.from_bytes(raw_bitfield, byteorder="big")).strip('0b')
        except:
            raw_bitfield, = unpack(">{}s".format(len(message) - 5), message[5:])
            bitfield = bin(int.from_bytes(raw_bitfield, byteorder="big")).strip('0b')
        print(bitfield) 