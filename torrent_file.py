import os
import time
import requests
import socket
import urllib
import hashlib 
from struct import pack, unpack
from random import randint
import bcoding
from manager import Manager
import logging
import asyncio
import random

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
        self.uploaded = 0
        self.downloaded = 0
        self.left = 0
        self.files = list()
        self.init_files()
        self.peers = list()
        self.peer_id = self.get_peer_id()
        self.info_hash = self.get_info_hash()
        self.handshake_message = self.get_handshake()
        self.peer_manager = None

    def open_torrent_file(self, path_to_torrent):
        logging.info(f"opened {path_to_torrent}")
        with open(path_to_torrent, "rb") as f:
            torrent_content = bcoding.bdecode(f.read())
        return torrent_content

    def get_peer_id(self):
        # peer_id = bytes(random.randint(0, 255) for _ in range(20))
        # print("peer id is", peer_id)
        # return peer_id
        peer_id = '-PY0001-' + ''.join([str(randint(0, 9)) for _ in range(12)])
        print("peer id is", peer_id)
        return peer_id.encode()

    def get_info_hash(self):
        raw_info_hash = bcoding.bencode(self.torrent_content['info'])
        return hashlib.sha1(raw_info_hash).digest()

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
        try:
            tracker = self.torrent_content['announce']
        except:
            raise Exception("#TODO if announce-list instead of announce")
        response = self.send_announce(tracker)
        self.handle_addresses(response)
        #
        if(len(self.peers)) > 0:
            logging.info(f"{len(self.peers)} peers were found.")
        else:
            logging.error("no peers were found")
            
    def send_announce(self, tracker):
        # port might be not neccesary
        params = {
            'info_hash': self.info_hash,
            'port': 6889,
            'peer_id': self.peer_id,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'event': 1,
            #'compact': 1,
        }
        query_string = urllib.parse.urlencode(params)
        url = f"{tracker}?{query_string}"
        response = requests.get(url)
        #print(response.text)
        return response

    def handle_addresses(self, response):
        """
        Parses addresses to ip and port that was send by tracker
        """
        self.peers = bcoding.bdecode(response.text)["peers"]

if __name__ == "__main__":
    torrent_instance = Torrent("torrent_example.torrent")
    torrent_instance.get_peers()
    manager_instance = Manager(torrent_instance)
    asyncio.run(manager_instance.start())

