import asyncio

class SVDRP:
    def __init__(self, host: str = "127.0.0.1", port: int = 6419):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.encoding = 'UTF-8'
        self.space = ord(' ') # space as byte value

    async def open_connection(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        greeting = await self.reader.readline()
        _, encoding = greeting.rsplit(b'; ', maxsplit=1)
        self.encoding  = encoding.rstrip().decode()


    async def close_connection(self):
        if self.writer:
            _ = await self.send_cmd("QUIT")
            self.writer.close()
            await self.writer.wait_closed()

    async def read_response(self) -> list[bytes]:
        if not self.reader:
            raise TypeError("trying to use reader without establishing the connection first")
        response = []
        while r := (await self.reader.readline()).strip():
            response.append(r[4:])
            if r[3] == self.space: # if the fourth position is a space, VDR is done with the response
                break
        return response

    async def send_cmd(self, cmd: str) -> list[bytes]:
        if not self.writer:
            raise TypeError("trying to use reader without establishing the connection first")
        self.writer.write(f"{cmd}\r\n".encode(self.encoding))
        await self.writer.drain()
        response = await self.read_response()
        return response

    async def __aenter__(self):
        await self.open_connection()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close_connection()

        


async def send_svdrpcommand(cmd: str, host: str = '127.0.0.1', port: int = 6419):
    space = ord(' ') # space as byte value
    async def send_cmd(cmd: str, encoding) -> None:
        writer.write(f"{cmd}\r\n".encode(encoding))
        await writer.drain()

    async def read_response() -> list[bytes]:
        response = []
        while r := (await reader.readline()).strip():
            response.append(r)
            if r[3] == space: # if the fourth position is a space, VDR is done with the response
                break
        return response
    
    async def quit() -> None:
        await send_cmd("QUIT", encoding)
        _ = await read_response()
        writer.close()
        await writer.wait_closed()

    reader, writer = await asyncio.open_connection(host, port)
    greeting = await reader.readline()
    _, encoding = greeting.rsplit(b'; ', maxsplit=1)
    encoding  = encoding.rstrip().decode()

    await send_cmd(cmd, encoding)
    response = await read_response()
    await quit()
    return response