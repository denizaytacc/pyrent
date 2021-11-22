import socket
from struct import pack, unpack
from random import randint

class UdpConnection(object):
    """
    Offset  Size            Name            Value
    0       64-bit integer  connection_id   0x41727101980
    8       32-bit integer  action          0 // connect
    12      32-bit integer  transaction_id  ? // random
    16
    """

    def __init__(self):
        self.connection_id = pack('>q', 0x41727101980)
        self.action = pack('>l', 0)
        self.transaction_id = pack('>l', randint(0, 1000))

    def return_buffer(self):
        return (self.connection_id + self.action + self.transaction_id)


class UdpAnnounce(object):
    """
    Choose a random transaction ID.
    Fill the announce request structure.
    Send the packet.
    Offset  Size    Name    Value
    0       64-bit integer  connection_id   // connection id from the UDP connect
    8       32-bit integer  action          1 // announce
    12      32-bit integer  transaction_id  // random
    16      20-byte string  info_hash       // 20 byte info hash of the file
    36      20-byte string  peer_id         // 20 byte string peer id
    56      64-bit integer  downloaded      // Total amount downloaded so far, represented in base ten in ASCII.
    64      64-bit integer  left            // Number of bytes this client still has to download, represented in base ten in ASCII. Tracker will only response with leechers if left => 0
    72      64-bit integer  uploaded        // Total amount uploaded so far, represented in base ten in ASCII.
    80      32-bit integer  event           0 // 0: none; 1: completed; 2: started; 3: stopped
    84      32-bit integer  IP address      0 // default
    88      32-bit integer  key             // random
    92      32-bit integer  num_want        -1 // default
    96      16-bit integer  port            // between 6881 - 6889 (inclusive)
    98
    """
    
    def __init__(self, connection_id, info_hash, peer_id, left):
        self.connection_id = connection_id
        self.action = pack('>l', 1)
        self.transaction_id = pack('>l', randint(0, 1000))
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.downloaded = pack('>q', 0)
        self.left = pack('>q', left)
        self.uploaded = pack('>q', 0)
        self.event = pack('>l', 0)
        self.ip_address = pack('>l', 0)
        self.key = pack('>l', randint(0, 1000))
        self.num_want = pack('>l', -1)
        self.port = pack(">h", 6881)
        # self.action = data_to_bytes(4, 1)
        # self.transaction_id = data_to_bytes(4, random.randint(0, 1000))
        # self.info_hash = info_hash
        # self.peer_id = peer_id
        # self.downloaded = data_to_bytes(8, 0)
        # self.left = data_to_bytes(8, left)
        # self.uploaded = data_to_bytes(8, 0)
        # self.event = data_to_bytes(4, 0)
        # self.ip_address = data_to_bytes(4, 0)
        # self.key = data_to_bytes(4, random.randint(0, 1000))
        # self.num_want = data_to_bytes(4, 30)
        # self.port = data_to_bytes(2, 6881)

    def return_buffer(self):
        return (self.connection_id + self.action + self.transaction_id + self.info_hash + self.peer_id + self.downloaded +
                self.left + self.uploaded + self.event + self.ip_address + self.key + self.num_want + self.port)