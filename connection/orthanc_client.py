import httpx


class OrthancClient:
    def __init__(self, url=None, username=None, password=None):
        self.url = url
        self.client = httpx.AsyncClient(verify=False)

    def init(self, url):
        self.url = url

    async def get_simplified_tags(self, level, uuid):
        res = await self.client.get(f"{self.url}/{level}/{uuid}/simplified-tags")
        res.raise_for_status()
        return res.json()

    async def find(self, body):
        res = await self.client.post(f"{self.url}/tools/find", json=body)
        res.raise_for_status()
        return res.json()

    async def retrieve(self, level, uuid, asset=None):
        if asset is None:
            res = await self.client.get(f"f{self.url}/{level}/{uuid}")
        else:
            res = await self.client.get(f"f{self.url}/{level}/{uuid}/{asset}")
        res.raise_for_status()
        return res

    async def upload(self, data):
        res = await self.client.post(f"{self.url}/instances", content=data)
        res.raise_for_status()
        return res.json()

    async def get(self, path: str):
        res = await self.client.get(f"{self.url}{path}")
        res.raise_for_status()
        return res.json()

    async def ping(self):
        res = await self.client.get(f"{self.url}/system")
        res.raise_for_status()
