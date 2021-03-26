from dynaconf import settings
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch([settings.ELASTICSEARCH_HOST])


async def connect():
    await es.ping()


async def disconnect():
    await es.close()
