from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import re
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "discovered_opportunities.json"

FEEDS = {
    "Google News - Scholarships":
        "https://news.google.com/rss/search?q=scholarships+Africa+students&hl=en&gl=US&ceid=US:en",

    "Google News - Jobs Tanzania":
        "https://news.google.com/rss/search?q=jobs+Tanzania&hl=en&gl=US&ceid=US:en",

    "Google News - Internships Africa":
        "https://news.google.com/rss/search?q=internships+Africa+students&hl=en&gl=US&ceid=US:en",

    "Google News - Free Courses":
        "https://news.google.com/rss/search?q=free+online+courses+students&hl=en&gl=US&ceid=US:en",
}


KEYWORDS = [
    "scholarship",
    "scholarships",
    "fully funded",
    "fellowship",
    "grant",
    "internship",
    "internships",
    "job",
    "jobs",
    "career",
    "course",
    "courses",
    "training",
    "students",
    "africa",
    "tanzania",
    "international students",
]


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_date(value):
    if not value:
        return ""

    try:
        return parsedate_to_datetime(value).astimezone(
            timezone.utc
        ).isoformat()
    except Exception:
        return value


def fetch_feed(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "OpportunityBridge Opportunity Discovery Bot/1.0"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def parse_feed(xml_data, source_name):
    root = ET.fromstring(xml_data)

    items = []

    for item in root.findall(".//item"):
        title = clean_text(
            item.findtext("title", default="")
        )

        link = clean_text(
            item.findtext("link", default="")
        )

        description = clean_text(
            item.findtext("description", default="")
        )

        published = parse_date(
            item.findtext("pubDate", default="")
        )

        combined = (
            f"{title} {description}"
        ).lower()

        matched_keywords = [
            keyword
            for keyword in KEYWORDS
            if keyword.lower() in combined
        ]

        if not matched_keywords:
            continue

        items.append(
            {
                "title": title,
                "source": source_name,
                "source_url": link,
                "published": published,
                "matched_keywords": matched_keywords,
                "discovered_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "status": "needs_verification",
            }
        )

    return items


def remove_duplicates(items):
    unique = {}
    for item in items:
        key = (
            item["title"]
            .strip()
            .lower()
        )

        if key and key not in unique:
            unique[key] = item

    return list(unique.values())


def main():
    all_items = []

    print("=" * 60)
    print("OPPORTUNITYBRIDGE DISCOVERY SYSTEM")
    print("=" * 60)

    for source_name, feed_url in FEEDS.items():
        print(f"\nChecking: {source_name}")

        try:
            xml_data = fetch_feed(feed_url)
            items = parse_feed(
                xml_data,
                source_name
            )

            print(f"Found: {len(items)} relevant items")

            all_items.extend(items)

        except Exception as error:
            print(f"ERROR: {error}")

    all_items = remove_duplicates(all_items)

    all_items.sort(
        key=lambda item: item.get(
            "published",
            ""
        ),
        reverse=True,
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "total": len(all_items),

        "items": all_items[:100],
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print(
        f"Saved {len(all_items[:100])} discoveries."
    )
    print(f"Output: {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
