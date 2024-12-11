from fastapi import Request


async def api_health(req: Request) -> dict[str, str]:
    return {"status": "ok"}


api_route_kwargs = {
    "path": "/health",
    "endpoint": api_health,
    "methods": ["GET"],
}
