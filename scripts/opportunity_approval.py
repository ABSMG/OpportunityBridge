from pathlib import Path
from urllib.parse import urlparse
import json


ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "verified_opportunities.json"
OUTPUT = ROOT / "data" / "approved_opportunities.json"


REQUIRED_KEYWORDS = {
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
}


def valid_url(url):
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def has_opportunity_keyword(item):
    title = item.get("title", "").lower()

    matched = [
        keyword.lower()
        for keyword in item.get(
            "matched_keywords",
            []
        )
    ]

    combined = f"{title} {' '.join(matched)}"

    return any(
        keyword in combined
        for keyword in REQUIRED_KEYWORDS
    )


def approve(item):
    title = item.get("title", "").strip()
    source_url = item.get("source_url", "").strip()

    verification_status = item.get(
        "verification_status",
        ""
    )

    if not title:
        return False, "Missing title"

    if not valid_url(source_url):
        return False, "Invalid source URL"

    if verification_status != "verified_source":
        return False, "Source has not passed verification"

    if not has_opportunity_keyword(item):
        return False, "Opportunity type not recognized"

    return True, "Passed approval checks"


def main():
    print("=" * 60)
    print("OPPORTUNITYBRIDGE APPROVAL ENGINE")
    print("=" * 60)

    if not INPUT.exists():
        raise SystemExit(
            "ERROR: verified_opportunities.json was not found."
        )

    data = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    items = data.get("items", [])

    approved = []
    rejected = []

    for item in items:
        is_approved, reason = approve(item)

        updated = dict(item)

        if is_approved:
            updated["approval_status"] = "approved"
            updated["approval_reason"] = reason
            approved.append(updated)
        else:
            updated["approval_status"] = "rejected"
            updated["approval_reason"] = reason
            rejected.append(updated)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result = {
        "approved_at": data.get(
            "verified_at",
            ""
        ),
        "total_checked": len(items),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "approved_items": approved,
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Checked: {len(items)}")
    print(f"Approved: {len(approved)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Saved: {OUTPUT}")

    print("=" * 60)


if __name__ == "__main__":
    main()
