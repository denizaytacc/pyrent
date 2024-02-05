## Pyrent
Pyrent implements bittorrent, which is a peer-to-peer file sharing protocol. Famous clients include utorrent, qbittorrent and transmission.

## How does it work?

Every torrent file includes a bencoded dictionary including the meta information about the file(s).
One of these information is the tracker url, which accepts GET requests and returns the peer list as bencoded dictionary. 
After getting the peer list bittorrent client tries to initiate a connection by sending each peer a handshake that includes hash info of the desired file(also with other info). The data protocol used here is TCP. If the peer is willing to take this connection to next level they send an another handshake back. 
Sometimes right after the handshake peer might send bitfield that represents the pieces(usually 512KB) they have, if not the client might ask it later. Every connection starts choked as a state, the client should sen an interested message and checks if the client is open to sending files. If the peer sends an unchoke message back the client should be able to download files. The program uses asyncio instead of sockets + threading because of long i/o bound.

  

## Prerequisites
* requests
* bcoding

## References:

https://web.archive.org/web/20220716002236/bittorrent.org/beps/bep_0003.html Creator's original specifications

https://wiki.theory.org/BitTorrentSpecification More detailed information about the protocol

https://docs.python.org/3/library/asyncio.html Python 3 asyncio documentation