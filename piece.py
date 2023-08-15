import math
import hashlib
from utils import BLOCK_SIZE
from block import Block


class Piece(object):
    def __init__(self, piece_index, piece_length, piece_hash):
        self.piece_index = piece_index
        self.piece_length = piece_length
        self.piece_hash = piece_hash
        self.data = b""
        self.piece_offset = piece_index * piece_length
        self.blocks = self.init_blocks()

    def __repr__(self):
        return f"Piece {piece_index} with length {self.piece_length}"

    def is_piece_completed(self):
        self.data = construct_piece()
        if is_piece_hash_correct:
            return True
        else:
            LOGGER.debug(f"Error! Piece {self.piece_index} had invalid hash.")
            self.blocks = init_blocks()
            return False

    def is_piece_hash_correct(self):
        piece_hash = hashlib.sha1(data).digest()
        if piece_hash == self.piece_hash:
            return True

    def update_piece(self):
        pass

    def construct_piece(self):
        data = b""
        for block in self.blocks:
            data += block.data
        return data

    def init_blocks(self):
        number_of_blocks = int(math.ceil(float(self.piece_length) / BLOCK_SIZE))
        last_block = number_of_blocks - 1
        blocks = list()
        for idx in range(number_of_blocks):
            if idx == last_block:
                last_block_size = self.piece_length % BLOCK_SIZE
                if last_block_size == 0:
                    last_block_size = BLOCK_SIZE
                blocks.append(Block(idx, last_block_size))
            else:
                blocks.append(Block(idx, BLOCK_SIZE))
        return blocks
