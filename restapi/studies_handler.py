from fastapi import APIRouter, Depends, File, Form, Request, Security, UploadFile
from fastapi.responses import JSONResponse
from restapi import studies_model
from connection.models import TokenData
from middleware.authenticate import verify_scopes
from middleware.permission import require_perms
from loguru import logger
from dynaconf import settings

router = APIRouter(dependencies=[Depends(require_perms(["studies#create"]))])


@router.post("/upload")
async def handle_upload(
    file: UploadFile = File(...),
        project_id: str = Form(...),
        token_data: TokenData = Security(verify_scopes, scopes=["profile"]),
        request: Request = Request,
):

    try:
        creator_id = token_data.sub
        jwt_token = request.headers["authorization"]
        data = await file.read()
        ex = await studies_model.process(
            origin_bytes=data,
            project_id=project_id,
            creator_id=creator_id,
            jwt_token=jwt_token,
        )

        logger.info("{0} {1}", file.filename, len(data))

        if ex is None:
            return JSONResponse({"message": "Upload success"}, status_code=200)
        else:
            return JSONResponse({"message": f"{ex}"}, status_code=500)
    except Exception as ex:
        logger.exception(ex)
        return JSONResponse({"message": f"{ex}"}, status_code=500)

