from beren import Orthanc
from dynaconf import settings

from .elasticsearch_client import es
from .keycloak_client import KeycloakClient
from .orthanc_client import OrthancClient
from .redis_client import Redis

oc = OrthancClient()  # noqa
oc2 = Orthanc(settings.ORTHANC_API_URI)

KEYCLOAK_HOST = settings.get("KEYCLOAK_HOST")
KEYCLOAK_CLIENT_ID = settings.get("KEYCLOAK_CLIENT_ID")
KEYCLOAK_REALM = settings.get("KEYCLOAK_REALM")
KEYCLOAK_SECRET_KEY = settings.get("KEYCLOAK_SECRET_KEY")
keycloak_client = KeycloakClient(url=KEYCLOAK_HOST, realm=KEYCLOAK_REALM)

redis = Redis()

public_key = None


def load_public_key():
    global public_key
    if public_key is None:
        jwt_keys = keycloak_client.get_keys()
        tmp = jwt_keys["public_key"]
        public_key = str.encode(f"-----BEGIN PUBLIC KEY-----\n{tmp}\n-----END PUBLIC KEY-----")
    return public_key
