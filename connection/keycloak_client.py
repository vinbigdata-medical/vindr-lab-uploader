import httpx
import requests
from keycloak import KeycloakOpenID


class KeycloakClient:
    url: str = None
    username: str = None
    password: str = None
    client: httpx.AsyncClient = None
    keycloak_openid: KeycloakOpenID = None
    realm: str = None
    secret_key: str = None

    def __init__(self, url=None, username=None, password=None, client_id=None, realm=None, secret_key=None):
        self.url = url
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(verify=False)
        self.realm = realm
        self.client_id = client_id
        self.secret_key = secret_key
        self.keycloak_openid = KeycloakOpenID(server_url=url,
                                              client_id=client_id,
                                              realm_name=realm,
                                              client_secret_key=secret_key)

    def get_keys(self):
        endpoint = f"{self.url}/realms/{self.realm}"
        res = requests.get(url=endpoint)
        res.raise_for_status()
        return res.json()
