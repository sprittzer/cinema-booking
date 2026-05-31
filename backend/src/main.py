import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .booking.api import router as booking_router
from .booking.providers import BookingProvider
from .catalog.api import actors_router
from .catalog.api import router as catalog_router
from .catalog.providers import CatalogProvider
from .common.config import config
from .common.providers import ConfigProvider, DatabaseProvider
from .identity.api import router as identity_router
from .identity.providers import IdentityProvider
from .scheduling.api import halls_router, sessions_router
from .scheduling.providers import SchedulingProvider

app = FastAPI(title="НеКино API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.include_router(identity_router)
app.include_router(catalog_router)
app.include_router(actors_router)
app.include_router(halls_router)
app.include_router(sessions_router)
app.include_router(booking_router)

container = make_async_container(
    ConfigProvider(),
    DatabaseProvider(),
    IdentityProvider(),
    CatalogProvider(),
    SchedulingProvider(),
    BookingProvider(),
)
setup_dishka(container, app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=config.host, port=config.port, reload=config.debug)
