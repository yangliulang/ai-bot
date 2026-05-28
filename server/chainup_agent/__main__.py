import uvicorn

from chainup_agent.core.config import get_settings


def run() -> None:
    s = get_settings()
    uvicorn.run(
        "chainup_agent.main:app",
        host=s.api_host,
        port=s.api_port,
        reload=s.debug,
    )


if __name__ == "__main__":
    run()
