#!/usr/bin/env python3
"""One-off path rewriter for domain restructure. Run from repo root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    skip = {".cursor", ".git", "node_modules", ".specify/scripts/_rewrite_paths.py"}
    for path in ROOT.rglob("*.md"):
        if any(s in path.parts for s in skip):
            continue
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        o = text

        # Global URL-like path segments (longest first)
        reps = [
            ("requirements/domains/trading-agent/", "requirements/domains/agent/trading-agent/"),
            ("requirements/domains/onboarding/", "requirements/domains/agent/onboarding/"),
            ("requirements/domains/billing/billing.md", "requirements/domains/admin/billing-management/overview.md"),
            ("requirements/domains/observability/observability.md", "requirements/observability/overview.md"),
            ("requirements/channels/telegram.md", "requirements/domains/agent/telegram/overview.md"),
            ("domains/trading-agent/", "domains/agent/trading-agent/"),
            ("domains/onboarding/", "domains/agent/onboarding/"),
            ("domains/billing/billing.md", "domains/admin/billing-management/overview.md"),
            ("domains/billing/", "domains/admin/billing-management/"),
            ("domains/observability/observability.md", "observability/overview.md"),
            ("domains/admin-console/", "domains/admin/agent-management/"),
            ("admin-console/prompt-management.md", "admin/prompt-management/overview.md"),
            ("admin-console/Config.md", "admin/management-console-v1-prd.md"),
            ("admin-console/", "admin/agent-management/"),
            ("channels/telegram.md", "domains/agent/telegram/overview.md"),
            ("design/decisions/", "design/adr/"),
            ("./decisions/", "./adr/"),
            ("../design/decisions/", "../design/adr/"),
            ("../../design/decisions/", "../../design/adr/"),
            ("../../../design/decisions/", "../../../design/adr/"),
            ("../../design/overview.md", "../../design/architecture.md"),
            ("../design/overview.md", "../design/architecture.md"),
            ("`design/overview.md`", "`design/architecture.md`"),
            ("design/overview`", "design/architecture`"),
            ("`design/overview`", "`design/architecture`"),
        ]
        for a, b in reps:
            text = text.replace(a, b)

        # trading-agent relative → admin / observability
        p = str(path.relative_to(ROOT))
        if "specs/requirements/domains/agent/trading-agent/" in p:
            text = text.replace("](../billing/billing.md)", "](../../admin/billing-management/overview.md)")
            text = text.replace("](../admin-console/Config.md)", "](../../admin/management-console-v1-prd.md)")
            text = text.replace("](../admin-console/", "](../../admin/agent-management/")
            text = text.replace("](../observability/observability.md)", "](../../../observability/overview.md)")
            text = text.replace("(../admin-console/Config.md)", "(../../admin/management-console-v1-prd.md)")
            text = text.replace("`../admin-console/", "`../../admin/agent-management/")
        if str(path.relative_to(ROOT)).startswith("specs/requirements/domains/admin/agent-management/"):
            text = text.replace("](../billing/billing.md)", "](../billing-management/overview.md)")
            text = text.replace("](../trading-agent/", "](../../agent/trading-agent/")
            text = text.replace("](../onboarding/", "](../../agent/onboarding/")
            text = text.replace("](../observability/observability.md)", "](../../../observability/overview.md)")
            text = text.replace("](../channels/", "](../../agent/telegram/")
            text = text.replace("](prompt-management.md)", "](../prompt-management/overview.md)")
            text = text.replace("](Config.md)", "](../management-console-v1-prd.md)")
            text = text.replace("[`Config.md`]", "[`management-console-v1-prd.md`]")
        if "specs/requirements/domains/admin/prompt-management/" in p:
            text = text.replace("](../admin-console/", "](../agent-management/")
            text = text.replace("](../trading-agent/", "](../../agent/trading-agent/")
        if "specs/requirements/domains/agent/telegram/" in p:
            text = text.replace("](../domains/trading-agent/", "](../trading-agent/")
            text = text.replace("](../domains/onboarding/", "](../onboarding/")
            text = text.replace("](../domains/billing/", "](../../admin/billing-management/")
            text = text.replace("](../channels/telegram.md)", "](overview.md)")

        if text != o:
            path.write_text(text, encoding="utf-8")
            print("updated", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
