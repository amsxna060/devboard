from exceptions import NotFoundError,ForbiddenError,BusinessError
from fastapi.responses import JSONResponse

async def handle_not_found_error(request, exc: NotFoundError):
    return JSONResponse(
        content={
        "error" : str(exc),
        "detail": f"{exc.resource} with id {exc.id} not found",
        "request_id":getattr(request.state, "request_id", "unknown")
        }
        ,status_code=404
        )

async def handle_forbidden_error(request, exc: ForbiddenError):
    return JSONResponse(
        content={
        "error" : exc.message,
        "detail": f"{exc.message}",
        "request_id":getattr(request.state, "request_id", "unknown")
        }
        ,status_code=403
        )
async def handle_business_error(request, exc: BusinessError):
    return JSONResponse(
        content={
        "error" : exc.message,
        "detail": f"{exc.message}",
        "request_id":getattr(request.state, "request_id", "unknown")
        }
        ,status_code=exc.status_code
        )