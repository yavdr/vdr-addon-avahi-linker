import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.post('/chan/{channel_number}')
async def svdrpcommand(channel_number: int) -> list[str]:
    r = await send_svdrpcommand(cmd=f"chan {channel_number}")
    return r
    


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
    response = [e.decode(errors="ignore") for e in response]
    return response


async def main():
    print(*await send_svdrpcommand(cmd='UPDR'))

#asyncio.run(main())
