"""Tests for ngrok local API URL helper CLI."""

from chainup_agent.cli.print_ngrok_https_base import pick_https_public_url


def test_pick_https_public_url_single_tunnel_no_port() -> None:
    tunnels = [
        {"proto": "http", "public_url": "http://ignored.example"},
        {
            "proto": "https",
            "public_url": "https://abc.ngrok-free.app/",
            "config": {"addr": "http://localhost:8080"},
        },
    ]
    assert pick_https_public_url(tunnels, upstream_port=None) == "https://abc.ngrok-free.app"


def test_pick_https_public_url_empty() -> None:
    assert pick_https_public_url([], upstream_port=None) is None
    tunnels_http = [{"proto": "http", "public_url": "http://x"}]
    assert pick_https_public_url(tunnels_http, upstream_port=None) is None


def test_pick_https_public_url_ambiguous_requires_port() -> None:
    tunnels = [
        {
            "proto": "https",
            "public_url": "https://a.ngrok.example/",
            "config": {"addr": "http://127.0.0.1:8080"},
        },
        {
            "proto": "https",
            "public_url": "https://b.ngrok.example/",
            "config": {"addr": "http://localhost:5174"},
        },
    ]
    assert pick_https_public_url(tunnels, upstream_port=None) is None
    assert pick_https_public_url(tunnels, upstream_port=8080) == "https://a.ngrok.example"
    assert pick_https_public_url(tunnels, upstream_port=5174) == "https://b.ngrok.example"
