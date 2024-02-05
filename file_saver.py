import asyncio
import utils

class FileSaver(object):
    def __init__(self, torrent, queue):
        self.file_name = torrent.files[0]
        self.file = open(self.file_name, "wb")
        self.running = True
        self.pieces_to_save = queue
        asyncio.ensure_future(self.start_save())

    async def start_save(self):
        print("file", self.file)
        while self.running:
            piece = await self.pieces_to_save.get()
            print("Received", piece)
            if piece is None:
                self.running = False
            else:
                print("Processing: ", piece)
                self.file.seek(piece.offset)
                self.f.write(piece.data)
            LOGGER.debug(f"Saved piece {piece.piece_index} to the disk")
            self.pieces_to_save.task_done()
            
        self.file.close()
