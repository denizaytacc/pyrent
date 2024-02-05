import asyncio
from struct import unpack
import socket
from utils import BLOCK_SIZE, LOGGER
from message import Message


class Peer(object):
    def __init__(self, ip, port, number_of_pieces):
        self.ip = ip
        self.port = port
        self.writer = None
        self.reader = None
        self.choked = True
        self.interested = False
        self.connected = False
        self.handshaken = False
        self.pieces = dict((idx, 0) for idx in range(0, number_of_pieces))

    async def close_connection(self):
            LOGGER.debug(f"closed the connection with {self.ip} {self.port}")
            self.writer.close()
            await writer.wait_closed()

    async def send_handshake(self, message):
        data = await self.send_message(message)
        if data:
            received_handshake = data[:68]
            seeder_status = False
            if len(received_handshake) == 68 and b'BitTorrent protocol' in received_handshake:
                r2 = None
                self.handshaken = True
                handshake = data[:68]
                LOGGER.debug(f"handshake with {self.ip}:{self.port} is successful")

                if len(data) > 68:
                    bitfield = self.parse_message(data[68:])
                    self.pieces = dict((idx, int(bitfield[idx])) for idx in range(0, len(bitfield)))
                    print("pc", self.pieces)
            else:
                LOGGER.error(f"peer {self.ip} {self.port} sent invalid handshake")
                self.connected = False
        else:
            LOGGER.debug(f"peer didn't accept the handshake {self.ip} {self.port}")

    async def send_message(self, message):
        if self.connected == False:
            try:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.ip, self.port), 10)
                LOGGER.debug(f"successfully connected to {self.ip}:{self.port}")
                self.connected = True
            except:
                LOGGER.info(f"error while connecting to the {self.ip}:{self.port}")
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
                    buffer = await asyncio.wait_for(self.reader.read(BLOCK_SIZE), 10)
                #print(buffer)
                if b"BitTorrent protocol" not in message: # means it wasn't a handshake and should be parsed
                    self.parse_message(buffer)
                return buffer

            except Exception as e:
                print(e)

    def parse_message(self, message):
        #print("received", message)
        message_length_ = int.from_bytes(message[:4], byteorder='big')
        id_ = int.from_bytes(message[4:5], byteorder='big')
        if id_ == 1:
            print("Client unchoked you!")
            self.choked = False

        if id_ == 5:
            print("Parsing bitfield")
            return self.parse_bitfield(message)

        


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
        return bitfield