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
        self.torrent_content = self.open_torrent_file(path_to_torrent)
        self.left = 0
        self.files = list()
        self.init_files()
        self.peers = list()
        self.peer_id = self.get_peer_id()
        self.info_hash = self.get_info_hash()
        self.handshake_message = self.get_handshake()
        self.UdpAnnounce = None
        self.connection_id = None
        self.peer_manager = None
        self.UdpConnection = UdpConnection()
        self.get_peers()

    def open_torrent_file(self, path_to_torrent):
        logging.info(f"opened {path_to_torrent}")
        with open(path_to_torrent, "rb") as f:
            torrent_content = bcoding.bdecode(f.read())
        return torrent_content

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
        raw_trackers = self.torrent_content['announce-list']
        trackers = [tracker for tracker in raw_trackers if tracker[0].startswith('udp')]
        for t in trackers:
            tracker = "".join(t) # Converting list -> str
            success = self.handle_udp(tracker)
            if success:
                break
        if(len(self.peers)) > 0:
            logging.info(f"{len(self.peers)} peers were found.")
        else:
            logging.error("no peers were found")
        self.peer_manager = PeerManager(self.handshake_message, self.torrent_content['info']['pieces'], self.peers)


    def handle_udp(self, tracker):
        """
        Receive the packet.
        Check whether the packet is at least 16 bytes.
        Check whether the transaction ID is equal to the one you chose.
        Check whether the action is connect.
        Store the connection ID for future use.
        """  
        message = self.UdpConnection.return_buffer()
        success = False
        tries = 0
        while tries < 5:
            data = self.send_message(tracker, message)
            if data:
                if len(data) >= 16 and self.UdpConnection.transaction_id == data[4:8]:
                    self.connection_id = data[8:]
                    self.UdpAnnounce = UdpAnnounce(self.connection_id, self.info_hash, self.peer_id, self.left)
                    self.send_announce(tracker, self.UdpAnnounce)
                    success = True
            else:
                logging.warning("UDPConnect wasn't successful, trying again.")
            tries += 1
        return success
    def send_message(self, tracker, message):
        """
        Send message over UDP protocol, given a tracker address and the message to deliver
        """
        try:
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
        except Exception as e:
            print("error", e)
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
            if [ip, port] not in self.peers:
                self.peers.append([ip, port])

if __name__ == "__main__":
    Torrent_ = Torrent("torrent_example.torrent")

