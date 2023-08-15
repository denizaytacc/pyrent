import asyncio
from collections import deque
from utils import BLOCK_SIZE
from peer import Peer
from file_saver import FileSaver
from piece import Piece
from message import Message

class Manager(object):
    def __init__(self, torrent, queue):
        self.torrent = torrent
        self.peers = [Peer(peer["ip"], peer["port"]) for peer in self.torrent.peers]
        self.handshake_message = self.torrent.handshake_message
        self.torrent_piece_length = self.torrent.torrent_content['info']['length']
        self.piece_length = self.torrent.torrent_content['info']['piece length']
        self.pieces_hash = self.torrent.torrent_content['info']['pieces']
        self.pieces = self.init_pieces()
        self.downloaded_pieces = [False for _ in range(len(self.pieces_hash) // 20)]
        self.pieces_to_save = queue
        self.finished = False

    # returns random piece and a peer that has the piece
    def get_random_piece(self):
        false_idx = [idx for idx, value in enumerate(self.downloaded_pieces) if value is False]
        if len(false_idx) > 0:
            piece_to_request = random.choice(false_idx)
            peer_to_request = random.choice([peer for peer in self.peers if peer.pieces[piece_to_request] == 1])
            if peer_to_request == None:
                pass # TODO
            else:
                return peer_to_request, piece_to_request
        else:
            pass
            #self.finished = True

    # requests piece from specific peer
    async def request_piece(self, peer, piece):
        pass
        #send_request_to_peer
        #get_whole_request
        #check_if_request_correct
        #save_block

    # returns random peer that has the piece with given index
    def get_owner_of_piece(self, piece_idx):
        peers_with_bitfields = [peer for peer in self.peers if len(peer.pieces) == self.len(downloaded_pieces)]
        for idx, peer in enumerate(self.peers):
            if len(peer.pieces) == self.len(downloaded_pieces) and peer[piece_idx] == True:
                return idx

        # if piece not existent it
        for idx, peer in enumerate(self.peers):
            if peer.connected:
                pass
                #sent have
                #check if has
                #return idx

    def init_pieces(self):
        pieces = list()
        number_of_pieces = len(self.pieces_hash) // 20
        last_piece = number_of_pieces
        for idx in range(number_of_pieces):
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
        # for peer in self.peers:
        #     await peer.send_handshake(self.handshake_message)
        

        while not self.finished:
            peer, piece = get_random_piece()
            piece = await request_piece(peer, piece)
            await self.pieces_to_save.put(piece)
            #await asyncio.sleep(1)

        await self.pieces_to_save.put(None)