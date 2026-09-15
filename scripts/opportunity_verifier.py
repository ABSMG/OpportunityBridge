from pathlib import Path
from urllib.parse import urlparse
import json
import re


ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "discovered_opportunities.json"
OUTPUT = ROOT / "data" / "verified_opportunities.json"


TRUSTED_DOMAIN_HINTS = [
    ".edu",
    ".ac.",
    ".gov",
    ".org",
    "un.org",
    "worldbank.org",
    "afdb.org",
    "mastercardfdn.org",
    "commonwealthscholarships",
    "erasmus-plus.ec.europa.eu",
]


OPPORTUNITY_KEYWORDS = [
    "scholarship",
    "scholarships",
    "fellowship",
    "grant",
    "internship",
    "internships",
    "job",
    "jobs",
    "course",
    "courses",
    "training",
]


def valid_url(url):
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def domain_looks_trusted(url):
    try:
        domain = urlparse(url).netloc.lower()

        return any(
            hint in domain
            for hint in TRUSTED_DOMAIN_HINTS
        )

    except Exception:
        return False


def contains_opportunity_keyword(item):
    text = (
        f"{item.get('title', '')} "
        f"{' '.join(item.get('matched_keywords', []))}"
    ).lower()

    return any(
        keyword in text
        for keyword in OPPORTUNITY_KEYWORDS
    )


def verify_item(item):
    title = item.get("title", "").strip()
    source_url = item.get("source_url", "").strip()

    if not title:
        return "rejected", "Missing title"

    if not valid_url(source_url):
        return "rejected", "Invalid source URL"

    if not contains_opportunity_keyword(item):
        return "needs_review", "Opportunity type unclear"

    if domain_looks_trusted(source_url):
        return "verified_source", "Source domain looks authoritative"

    return "needs_review", "Source requires manual verification"


def main():
    print("=" * 60)
    print("OPPORTUNITYBRIDGE VERIFICATION ENGINE")
    print("=" * 60)

    if not INPUT.exists():
        raise SystemExit(
            "ERROR: discovered_opportunities.json was not found."
        )

    data = json.loads(
        INPUT.read_text(encoding="utf-8")
    )

    discoveries = data.get("items", [])

    verified = []

    for item in discoveries:
        status, reason = verify_item(item)

        verified_item = dict(item)

        verified_item["verification_status"] = status
        verified_item["verification_reason"] = reason

        verified.append(verified_item)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result = {
        "verified_at": data.get(
            "generated_at",
            ""
        ),
        "total_checked": len(verified),
        "items": verified,
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Checked: {len(verified)}")
    print(f"Saved: {OUTPUT}")

    print("\nVerification summary:")

    for status in [
        "verified_source",
        "needs_review",
        "rejected",
    ]:
        count = sum(
            1
            for item in verified
            if item["verification_status"] == status
        )

        print(f"- {status}: {count}")

    print("=" * 60)


if __name__ == "__main__":
    main()
