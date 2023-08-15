import logging

BLOCK_SIZE = 2 ** 14 # 16,384 KB

logging.basicConfig(
    filename = "torrent_log.log",
    level = logging.DEBUG,
    format='%(asctime)s - %(message)s', 
    datefmt='%d-%b-%y %H:%M:%S',
)

LOGGER = logging.getLogger('')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
LOGGER.addHandler(console)
