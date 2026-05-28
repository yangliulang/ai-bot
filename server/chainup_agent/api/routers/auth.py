from chainup_agent.api.deps import AdminLoginDbSession, DbSession
from chainup_agent.api.schemas.auth import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRegisterRequest,
)
from chainup_agent.application.admin_console_login import admin_console_login
from chainup_agent.application.admin_console_register import admin_console_register
from chainup_agent.core.config import get_settings
from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["Auth — admin console"])


@router.post("/register", response_model=AdminLoginResponse)
async def admin_register(
    body: AdminRegisterRequest,
    session: DbSession,
) -> AdminLoginResponse:
    """
    **运营控制台（`admin/`）自助注册**，写入 **`admin_console_user`**（bcrypt）。

    **前提**：**`ADMIN_CONSOLE_AUTH_MODE=database`** 且 **`alembic upgrade head`** 已有表；
    **`503`** **`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`** 若非 database 模式。

    **准许条件**：（1）库中尚无任何控制台用户 —— 首张账号可无其它配置；
    （2）或 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`** —— 允许继续注册；
    **`403`** **`ADMIN_CONSOLE_REGISTRATION_DISABLED`** 否则。

    **冲突**：用户名已存在 **`409`** **`ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS`**。

    **成功**：**`200`** 体字段同 **`POST /api/auth/login`**。
    """
    return await admin_console_register(session, get_settings(), body)


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    body: AdminLoginRequest,
    session: AdminLoginDbSession,
) -> AdminLoginResponse:
    """
    **运营控制台（`admin/`）登录**。

    **`admin_console_auth_mode=env`（默认）**：凭证为环境变量 \
    `CHAINUP_AGENT_ADMIN_PANEL_USERNAME` / `PASSWORD`；未配置则 **503** \
    `ADMIN_CONSOLE_AUTH_DISABLED`。

    **`admin_console_auth_mode=database`**：账号在表 **`admin_console_user`**（bcrypt 口令）；\
    可用 **`POST /api/auth/register`**（首张或在开放注册模式下）或 **`chainup-agent-seed-admin`**；\
    未知用户 / 错误口令 / 禁用账号均为 **401** \
    `ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS`（不区分「是否存在」以防枚举）。

    **成功**：**200** — **`access_token`**、**`token_type`** **`bearer`**、**`username`**。

    **JWT（可选 · 推荐生产）**：配置 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）后：\
    **`access_token`** 为 HS256 JWT；**`/api/v1/admin/*`** 须 **`Authorization: Bearer`**，\
    否则 **401** **`ADMIN_CONSOLE_AUTH_REQUIRED`**。\
    **Secret 留空**：**`access_token`** 仍为随机串，Admin 路由不强制 Bearer（仅本地联调）。
    """
    return await admin_console_login(session, get_settings(), body)
