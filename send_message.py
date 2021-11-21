import asyncio 

async def send_message(ip, port, message):
    fut = asyncio.open_connection(ip, port)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout = 1)
        print(f'Send: {message!r}')
        writer.write(message)
        await writer.drain()
        buffer = b''
        buffer = await reader.read(4096)
        tries = 1
        while len(buffer) < 68 and tries < 10:
            tries += 1
            buffer = await reader.read(4096)

        print('Close the connection')
        writer.close()
        await writer.wait_closed()
        return buffer
        
        
    except OSError as error:
        print(error)
        return b""

    except ConnectionRefusedError as error:
        print(f"{ip} refused to connect! {error}")
        return b""

    except asyncio.TimeoutError:
        print(f"Connection to {ip} was unsuccessful!")
        return b""