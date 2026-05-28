"""Resolve public HTTPS base URL from a locally running ngrok agent (local API only)."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from typing import Any
from urllib.parse import urlparse

import httpx

DEFAULT_NGROK_TUNNELS_API = "http://127.0.0.1:4040/api/tunnels"


def fetch_tunnels(api_url: str, *, timeout_seconds: float = 5.0) -> list[dict[str, Any]]:
    """GET ngrok ``/api/tunnels`` JSON."""
    r = httpx.get(api_url, timeout=timeout_seconds)
    r.raise_for_status()
    try:
        data = r.json()
    except json.JSONDecodeError as e:
        raise ValueError("ngrok API response is not valid JSON") from e
    tunnels = data.get("tunnels") if isinstance(data, dict) else None
    if not isinstance(tunnels, list):
        return []
    return [t for t in tunnels if isinstance(t, dict)]


def tunnel_upstream_port(item: dict[str, Any]) -> int | None:
    cfg = item.get("config")
    if not isinstance(cfg, dict):
        return None
    addr = cfg.get("addr")
    if not isinstance(addr, str):
        return None
    trimmed = addr.strip()
    parsed = urlparse(trimmed if "://" in trimmed else f"http://{trimmed}")
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme in ("http", "https"):
        return 443 if parsed.scheme == "https" else 80
    return None


def _https_candidate_tunnels(
    tunnels: list[dict[str, Any]],
) -> list[tuple[int | None, str, dict[str, Any]]]:
    """Yield (upstream_port_if_known, normalized_public_https_url, raw_tunnel)."""
    out: list[tuple[int | None, str, dict[str, Any]]] = []
    for item in tunnels:
        if item.get("proto") != "https":
            continue
        raw = item.get("public_url")
        if not isinstance(raw, str):
            continue
        cleaned = raw.strip().rstrip("/")
        if not cleaned.lower().startswith("https://"):
            continue
        out.append((tunnel_upstream_port(item), cleaned, item))
    return out


def pick_https_public_url(
    tunnels: list[dict[str, Any]],
    *,
    upstream_port: int | None,
) -> str | None:
    """
    Resolve public URL for an HTTPS tunnel.
    ``upstream_port`` ``None``: only allowed when exactly one HTTPS tunnel exists.
    Otherwise match ``config.addr`` local port against ``upstream_port``.
    """
    candidates = _https_candidate_tunnels(tunnels)
    if not candidates:
        return None
    if upstream_port is None:
        if len(candidates) != 1:
            return None
        return candidates[0][1]

    matched = [normalized for sport, normalized, _ in candidates if sport == upstream_port]
    if len(matched) == 1:
        return matched[0]
    return None


def _default_public_base_upstream_port_when_ambiguous(candidates_len: int) -> int | None:
    """Prefer 8080 for PUBLIC_BASE_URL when ngrok exposes multiple HTTPS endpoints."""
    return 8080 if candidates_len > 1 else None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Print public HTTPS URLs from ngrok's local API (start ngrok separately). "
            "If several HTTPS tunnels are online, specify --tunnel-upstream-port "
            "(8080 = Agent API webhook, 5174 = Deeplink Vite)."
        ),
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_NGROK_TUNNELS_API,
        help=f"ngrok local API (default: {DEFAULT_NGROK_TUNNELS_API})",
    )
    parser.add_argument(
        "--tunnel-upstream-port",
        type=int,
        metavar="PORT",
        help=(
            "Select tunnel by local forwarded port (`config.addr`). "
            "When omitted with a single HTTPS tunnel, that tunnel is used; "
            "when omitted with multiple tunnels, --export/--dotenv default ASSUME 8080 for API URL."
        ),
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Print `export CHAINUP_AGENT_PUBLIC_BASE_URL=…`",
    )
    parser.add_argument(
        "--dotenv",
        action="store_true",
        help="Print `.env` line `CHAINUP_AGENT_PUBLIC_BASE_URL=…`",
    )
    parser.add_argument(
        "--dotenv-bind",
        action="store_true",
        help=("Print `.env` line TELEGRAM_BIND_PAGE_URL (default upstream port **5174**)."),
    )
    ns = parser.parse_args(argv)

    if sum(bool(x) for x in (ns.export, ns.dotenv, ns.dotenv_bind)) > 1:
        parser.error("use at most one of --export, --dotenv, --dotenv-bind")

    try:
        tunnels = fetch_tunnels(ns.api_url)
    except httpx.HTTPError as e:
        print(
            "Could not reach ngrok local API. Start ngrok in another terminal, e.g.:\n"
            "  ngrok http 8080\n"
            "  or merged endpoints (Agent + Deeplink), see README and "
            "`ngrok.chainupEndpoints.example.yml`.\n"
            f"  ({e})",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    candidates = _https_candidate_tunnels(tunnels)

    if not candidates:
        print(
            "No HTTPS tunnel found on this ngrok agent. "
            "Open http://127.0.0.1:4040 and verify a tunnel is up.",
            file=sys.stderr,
        )
        sys.exit(1)

    def resolve_upstream_for_public_base(*, explicit: int | None) -> int | None:
        if explicit is not None:
            return explicit
        if len(candidates) == 1:
            return None
        return _default_public_base_upstream_port_when_ambiguous(len(candidates))

    if ns.export or ns.dotenv:
        upstream = resolve_upstream_for_public_base(explicit=ns.tunnel_upstream_port)
        if upstream is None and len(candidates) != 1:
            print(
                "Several HTTPS tunnels are online; "
                "pass --tunnel-upstream-port for `CHAINUP_AGENT_PUBLIC_BASE_URL` "
                "(use 8080 for the ChainUp Agent API tunnel).",
                file=sys.stderr,
            )
            sys.exit(1)
        url = pick_https_public_url(tunnels, upstream_port=upstream)
        if not url:
            print(f"No HTTPS tunnel matched upstream port {upstream}.", file=sys.stderr)
            sys.exit(1)
        if ns.export:
            print(f"export CHAINUP_AGENT_PUBLIC_BASE_URL={shlex.quote(url)}")
        else:
            print(f"CHAINUP_AGENT_PUBLIC_BASE_URL={url}")

    elif ns.dotenv_bind:
        bind_upstream = ns.tunnel_upstream_port if ns.tunnel_upstream_port is not None else 5174
        url = pick_https_public_url(tunnels, upstream_port=bind_upstream)
        if not url:
            print(f"No HTTPS tunnel matched upstream port {bind_upstream}.", file=sys.stderr)
            sys.exit(1)
        print(f"CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL={url}/")

    else:
        upstream = ns.tunnel_upstream_port
        if upstream is None and len(candidates) > 1:
            print(
                "Several HTTPS tunnels are online; specify --tunnel-upstream-port PORT "
                "(e.g. `--tunnel-upstream-port 5174`).",
                file=sys.stderr,
            )
            sys.exit(1)
        url = pick_https_public_url(tunnels, upstream_port=upstream)
        if not url:
            print(
                "No matching HTTPS tunnel. "
                "Use --tunnel-upstream-port matching your local Deeplink/API port.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(url)


if __name__ == "__main__":
    main()
