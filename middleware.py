from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from uuid import uuid4
import logging

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request:Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4())[:8])
        request.state.request_id = request_id
        now = time.perf_counter()
        logger.info(f"Received {request.method} request for {request.url.path} with ID {request_id}")
        response = None
        try:
            response = await call_next(request)
        finally:
            duration = (time.perf_counter() - now)*1000 #time in ms
            logger.info(f"{request.method} {request.url.path} completed in {duration:.2f}ms with status {response.status_code if response else 'unknown'} and ID {request_id}")
            if duration > 1000:
                logger.warning(f"{request.url.path} is taking more 1sec, Time is {duration:.2f}ms")
        if not response:
            return JSONResponse(status_code=500, content={"error": "Internal error"})
        response.headers["X-Request-ID"] = request_id   
        return response
