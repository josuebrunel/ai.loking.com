from starlette.middleware.base import BaseHTTPMiddleware

from app.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):

    async def set_body(self, request):
        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def dispatch(self, request, call_next):
        await self.set_body(request)
        if request.method in ("POST", "PUT", "PATCH"):
            json_body = await request.json()
            logger.debug(f"{request.method} - {request.url.path}",
                         extra={"body": json_body})
        response = await call_next(request)
        return response
