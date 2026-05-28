from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness (extend with DB / deps checks)")
async def ready() -> dict[str, str]:
    return {"status": "ok"}
