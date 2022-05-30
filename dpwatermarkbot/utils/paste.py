from aiohttp import ClientSession


async def paste(content: str):
    """Paste the provided content to nekobin."""
    content = str(content)
    NEKO_URL = "https://nekobin.com/"
    async with ClientSession() as sess:
        async with sess.post(
            NEKO_URL + "api/documents",
            json={"content": content},
        ) as resp:
            if resp.status != 201:
                raise Exception("Error Pasting to Nekobin")

            response = await resp.json()
            key = response["result"]["key"]
            final_url = f"{NEKO_URL}{key}.txt"
            raw = f"{NEKO_URL}raw/{key}.txt"
    return final_url, raw
