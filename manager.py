import asyncio
import random
from collections import deque
from utils import BLOCK_SIZE
from peer import Peer
from file_saver import FileSaver
from piece import Piece
from message import Message

class Manager(object):
    def __init__(self, torrent, queue):
        self.torrent = torrent
        self.handshake_message = self.torrent.handshake_message
        self.torrent_piece_length = self.torrent.torrent_content['info']['length']
        self.piece_length = self.torrent.torrent_content['info']['piece length']
        self.pieces_hash = self.torrent.torrent_content['info']['pieces']
        self.number_of_pieces = len(self.pieces_hash) // 20
        self.peers = [Peer(peer["ip"], peer["port"], self.number_of_pieces) for peer in self.torrent.peers]
        self.pieces = self.init_pieces()
        self.downloaded_pieces = [False for _ in range(self.number_of_pieces)]
        self.pieces_to_save = queue
        self.finished = False

    # returns a random piece which has not been downloaded
    def get_random_piece(self):
        pieces_to_download = [idx for idx, value in enumerate(self.downloaded_pieces) if value is False]
        if len(pieces_to_download) > 0:
            piece_to_request = random.choice(pieces_to_download)
            return piece_to_request
        else:
            print("downlaoding is finished")
            self.finished = True

    # requests specific piece from specific peer
    async def request_piece(self, peer, piece):
        print("here")
        pass
        #send_request_to_peer
        #get_whole_request
        #check_if_request_correct
        #save_block

    # returns random peer that has the piece with given index
    def get_owner_of_piece(self, piece_to_request):
        # choose a peer with bitfield if exists
        peers_with_bitfields = [peer for peer in self.peers if len(peer.pieces) == len(self.downloaded_pieces)]
        print(peers_with_bitfields[0].pieces[piece_to_request])
        available_peers_for_piece = [peer for peer in peers_with_bitfields if peer.pieces[piece_to_request] == 1]
        peer_to_request = None
        if len(available_peers_for_piece) > 0:
            peer_to_request = random.choice(available_peers_for_piece)

        # if none of the peers with bitfield doesn't have piece, request it by sending a Have message
        for idx, peer in enumerate(self.peers):
            if peer.connected:
                pass
                #sent have
                #check if has
                #return idx
        return peer_to_request


    # initalize the pieces
    def init_pieces(self):
        pieces = list()
        last_piece = self.number_of_pieces
        for idx in range(self.number_of_pieces):
            start = idx * 20 
            end = start + 20
            if idx == last_piece:
                last_piece_length = self.torrent_piece_length % self.piece_length
                if last_piece_length == 0:
                    last_piece_length = self.piece_length
                pieces.append(Piece(idx, last_piece_length, self.pieces_hash[start:end]))
            else:
                pieces.append(Piece(idx, self.piece_length, self.pieces_hash[start:end]))
        return pieces


    async def start(self):
        print("total pieces:", len(self.downloaded_pieces))
        for peer in self.peers:
            await peer.send_handshake(self.handshake_message)
        

        while not self.finished:
            piece = self.get_random_piece()
            peer = self.get_owner_of_piece(piece)
            print(peer)
            piece = await self.request_piece(peer, piece)
            await self.pieces_to_save.put(piece)
            #await asyncio.sleep(1)

        await self.pieces_to_save.put(None)