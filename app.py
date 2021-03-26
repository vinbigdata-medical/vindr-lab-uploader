import uvicorn
from dynaconf import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from connection import elasticsearch_client, oc, redis
from restapi import studies_handler


def init_app(app: FastAPI):
    @app.on_event("startup")
    async def setup_db():
        await elasticsearch_client.connect()
        logger.info("Successfully connected to Elasticsearch")

        oc.init(settings.ORTHANC_API_URI)
        await oc.ping()
        logger.info("Successfully connected to Orthanc")

        await redis.init(settings.REDIS_URI)
        await redis.ping()
        logger.info("Successfully connect to Redis")

    @app.on_event("shutdown")
    async def shutdown_db():
        await elasticsearch_client.disconnect()


def create_app():
    app = FastAPI()
    init_app(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Access-Control-Allow-Headers",
            "Origin",
            "Accept",
            "X-Requested-With",
            "Content-Type",
        ],
    )
    app.include_router(studies_handler.router, prefix="/studies")
    return app


application = create_app()

if __name__ == "__main__":
    uvicorn.run(application, host="0.0.0.0", port=8082, debug=True)
