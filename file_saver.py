

class FileSaver(object):
    def __init__(self, torrent):
        self.file = torrent.files[0] ## handle multiple files later
        print("hello")
