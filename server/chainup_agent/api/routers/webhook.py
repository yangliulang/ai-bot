import hmac
import logging

from chainup_agent.application.telegram_inbound import acknowledge_inbound_webhook
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import Response

router = APIRouter(tags=["Webhook"])

logger = logging.getLogger(__name__)


def _telegram_path_token_equals(path_segment: str, configured: str) -> bool:
    """Constant-time equality; rejects length mismatch without throwing."""
    if len(path_segment) != len(configured):
        return False
    return hmac.compare_digest(path_segment, configured)


@router.post(
    "/webhook/telegram/{bot_token}",
    status_code=200,
    summary=(
        "Telegram updates (path token vs env; 200 ack; binding hint + bind-page URL "
        "button or dev-only bound-chat echo)"
    ),
)
async def telegram_webhook(
    bot_token: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    settings = get_settings()
    expected = settings.telegram_bot_token
    if not expected:
        raise AppError(
            code="TELEGRAM_WEBHOOK_NOT_CONFIGURED",
            message=(
                "Telegram webhook is disabled (set CHAINUP_AGENT_TELEGRAM_BOT_TOKEN in server/.env)"
            ),
            status_code=503,
        )
    if not _telegram_path_token_equals(bot_token, expected):
        raise AppError(
            code="NOT_FOUND",
            message="Not Found",
            status_code=404,
        )
    body = await request.body()
    logger.info("telegram_webhook_ingested content_length=%s", len(body))
    # Telegram expects a fast HTTP 200; outbound LLM / exchange reads can exceed client timeouts.
    if settings.telegram_webhook_inline_processing:
        await acknowledge_inbound_webhook(settings, expected, body)
    else:
        background_tasks.add_task(acknowledge_inbound_webhook, settings, expected, body)
    return Response(status_code=200)
