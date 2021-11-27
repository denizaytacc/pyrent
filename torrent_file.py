import os
import time
import requests
import socket
from urllib.parse import urlparse
import hashlib 
from struct import pack, unpack
from random import randint
import bcoding
from udp import UdpConnection, UdpAnnounce
from peer_manager import PeerManager
import logging



logging.basicConfig(
    filename = "torrent_log.log",
    level = logging.DEBUG,
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b-%y %H:%M:%S',
)

logging.getLogger('asyncio').setLevel(logging.WARNING)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class Torrent(object):
    def __init__(self, path_to_torrent):
        logging.info(f"Opened {path_to_torrent}")
        self.torrent_file, self.torrent_content = self.open_torrent_file(path_to_torrent)
        self.left = 0
        self.files = []
        self.trackers = self.torrent_content['announce-list']
        self.trackers = [tracker for tracker in self.trackers if tracker[0].startswith('udp')]
        self.info_hash = self.get_info_hash()
        self.peer_id = self.get_peer_id()
        self.UdpConnection = UdpConnection()
        self.UdpAnnounce = None
        self.connection_id = None
        self.peer_manager = None
        self.peers = []
        self.handshake_message = self.get_handshake()
        self.init_files()
        self.get_peers()

    def open_torrent_file(self, path_to_torrent):
        t_file = open(path_to_torrent, "rb")
        torrent_file = t_file.read()
        torrent_content = bcoding.bdecode(torrent_file)
        t_file.close()
        return torrent_file, torrent_content

    def get_info_hash(self):
        raw_info_hash = bcoding.bencode(self.torrent_content['info'])
        return hashlib.sha1(raw_info_hash).digest()

    def get_peer_id(self):
        peer_id = '-PY0001-' + ''.join([str(randint(0, 9)) for _ in range(12)])
        return peer_id.encode()

    def get_handshake(self):
        pstr = b"BitTorrent protocol"
        pstrlen = len(pstr)
        return pack(">B{}s8s20s20s".format(pstrlen), pstrlen, pstr, b'\x00\x00\x00\x00\x00\x00\x00\x00', self.info_hash, self.peer_id)

    def init_files(self):
        folder_name = self.torrent_content['info']['name']
        if not os.path.exists(folder_name):
            os.mkdir(f"{folder_name}")
        try:
            for f in self.torrent_content['info']['files']:
                self.files.append(f['path'])
                self.left += f['length']
        except:
            self.files.append(self.torrent_content['info']['name'])
            self.left += self.torrent_content['info']['length']

    def get_peers(self):
        for t in self.trackers:
            tracker = "".join(t) # Converting list -> str
            connection = self.handle_udp(tracker)
        if(len(self.peers)) > 0:
            logging.info(f"{len(self.peers)} peers were found.")
        else:
            logging.error("No peers were found")
        self.peer_manager = PeerManager(self.handshake_message, self.peers)


    def handle_udp(self, tracker):
        """
        Receive the packet.
        Check whether the packet is at least 16 bytes.
        Check whether the transaction ID is equal to the one you chose.
        Check whether the action is connect.
        Store the connection ID for future use.
        """  
        message = self.UdpConnection.return_buffer()
        while True:
            data = self.send_message(tracker, message)
            if len(data) >= 16 and self.UdpConnection.transaction_id == data[4:8]:
                break
            else:
                logging.warning("UDPConnect wasn't successful, trying againn.")
        self.connection_id = data[8:]
        self.UdpAnnounce = UdpAnnounce(self.connection_id, self.info_hash, self.peer_id, self.left)
        self.send_announce(tracker, self.UdpAnnounce)


    
    def send_message(self, tracker, message):
        """
        Send message over UDP protocol, given a tracker address and the message to deliver
        """
        parsed = urlparse(tracker)
        ip, port = socket.gethostbyname(parsed.hostname), parsed.port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(5)
        sock.sendto(message, (ip, port))
        data = b''
        while True:
            try:
                buffer = sock.recv(4096)
                if not buffer:
                    break

                data += buffer
            except:
                break 
        return data
         
    def send_announce(self, tracker, announce):
        """
        Receive the packet.
        Check whether the packet is at least 20 bytes.
        Check whether the transaction ID is equal to the one you chose.
        Check whether the action is announce.
        Do not announce again until interval seconds have passed or an event has occurred.
        """
        message = announce.return_buffer()
        data = self.send_message(tracker, message)
        
        if len(data) >= 20 and announce.transaction_id == data[4:8] and data[:4] == b'\x00\x00\x00\x01':
            action_ = unpack('>l', data[:4])
            transaction_id_ = unpack('>l', data[4:8])
            interval_ = unpack('>l', data[8:12])
            leechers_ = unpack('>l', data[12:16])
            seeders_ = unpack('>l', data[16:20])
            self.handle_addresses(data[20:])
            # print("*************************")
            # print("action: ", action_)
            # print("transaction_id: ", transaction_id_)
            # print("interval: ", interval_)
            # print("leechers: ", leechers_)
            # print("seeders: ", seeders_)
            
        else:
            logging.debug("Couldn't send the announce")

        
    def handle_addresses(self, data):
        """
        Parses addresses to ip and port that was send by tracker
        """
        addresses = []
        for i in range(int(len(data) / 6)):
            ip = socket.inet_ntoa(data[i:i + 4])
            raw_port = data[i + 4:i + 6]
            port = raw_port[1] + raw_port[0] * 256
            addresses.append([ip, port])
            #print("ip: ", ip, "port: ", port)
            if [ip, port] not in self.peers:
                self.peers.append([ip, port])

Torrent_ = Torrent("torrent_example.torrent")

