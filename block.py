from utils import BLOCK_SIZE

class Block(object):
    def __init__(self, block_index, block_length, block_data = b""):
        self.block_index = block_index
        self.block_offset = block_index * BLOCK_SIZE
        self.block_length = block_length
        self.data = block_data
    
    def update_block(self, data):
        self.data = data

    def __repr__(self):
        return f"Block {block_index} with offset {self.block_offset} and length {self.block_length}"