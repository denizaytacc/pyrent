from struct import pack, unpack

class Message(object):
    @staticmethod
    def Choke():
        return pack(">IB", 1, 0)

    @staticmethod
    def Unchoke():
        return pack(">IB", 1, 1)

    @staticmethod
    def Interested():
        return pack(">IB", 1, 2)

    @staticmethod
    def NotInterested():
        return pack(">IB", 1, 3)

    @staticmethod
    def Have(piece_index):
        return pack(">IBI", 5, 4, piece_index)

    @staticmethod
    def BitField(bitfield):
        bitfield_length = (bitfield.bit_length() + 7) // 8
        return pack(">IB{}s".format(bitfield_length), 1 + bitfield_length, 5, bitfield.to_bytes(bitfield_length, byteorder="big"))
    
    @staticmethod
    def Request(index, begin, length):
        return pack(">IBIII", 13, 6, index, begin, length)

    @staticmethod
    def Piece(index, begin, block, block_length):
        return pack(">IBII{}s".format(block_length), 9 + block_length, 7, index, begin, length)

    @staticmethod
    def Cancel(index, begin, length):
        return pack(">IBIII", 13, 8, index, begin, length)

    @staticmethod
    def Port(listen_port):
        return pack(">IBI", 3, 9, listen_port) 

class MessageParser(object):
    def __init__(self, msg):
        self.Messages = {
        0: "Choke",
        1: "Unchoke",
        2: "Interested",
        3: "NotInterested",
        4: "Have",
        5: "BitField",
        6: "Request",
        7: "Piece",
        8: "Cancel",
        9: "Port"
        }
        
        message_length_ = int.from_bytes(msg[:4], byteorder='big')
        id_ = int.from_bytes(msg[4:5], byteorder='big')
        message_name = self.Messages[id_]



