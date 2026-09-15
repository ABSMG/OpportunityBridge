from pathlib import Path
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, ElementTree
import subprocess


BASE_URL = "https://absmg.github.io"

ROOT = Path(__file__).resolve().parents[1]


# Pages that should NOT appear in Google sitemap.
EXCLUDED = {
    "404.html",
    "login.html",
    "logout.html",
    "register.html",
    "dashboard.html",
    "forgot-password.html",
    "reset-password.html",
    "privacy.html",
    "disclaimer.html",
}


# Priority for important OpportunityBridge pages.
PRIORITIES = {
    "index.html": "1.0",

    "scholarships.html": "0.9",
    "jobs.html": "0.9",
    "internships.html": "0.9",
    "courses.html": "0.9",
    "opportunities.html": "0.9",

    "skills.html": "0.8",
    "digital-skills.html": "0.8",
    "career-skills.html": "0.8",
    "computer-skills.html": "0.8",
    "data-skills.html": "0.8",
    "digital-marketing.html": "0.8",
    "web-development.html": "0.8",
    "ai-skills.html": "0.8",

    "about.html": "0.6",
    "contact.html": "0.5",
}


# Change frequency hints.
CHANGEFREQ = {
    "index.html": "daily",

    "scholarships.html": "daily",
    "jobs.html": "daily",
    "internships.html": "daily",
    "courses.html": "daily",
    "opportunities.html": "daily",

    "skills.html": "weekly",
    "digital-skills.html": "weekly",
    "career-skills.html": "weekly",
    "computer-skills.html": "weekly",
    "data-skills.html": "weekly",
    "digital-marketing.html": "weekly",
    "web-development.html": "weekly",
    "ai-skills.html": "weekly",

    "about.html": "monthly",
    "contact.html": "monthly",
}


def get_last_modified(path: Path) -> str:

    try:

        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%cs",
                "--",
                str(path.relative_to(ROOT)),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        value = result.stdout.strip()

        if value:
            return value

    except Exception:
        pass

    return datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    ).date().isoformat()


def url_for(path: Path) -> str:

    relative = path.relative_to(
        ROOT
    ).as_posix()

    if relative == "index.html":
        return BASE_URL + "/"

    return BASE_URL + "/" + relative


def should_include(path: Path) -> bool:

    if path.name in EXCLUDED:
        return False

    if path.name.startswith("_"):
        return False

    if not path.name.lower().endswith(".html"):
        return False

    return True


# Collect all public HTML pages.
pages = []

for path in ROOT.glob("*.html"):

    if should_include(path):
        pages.append(path)


# Homepage first, then alphabetical order.
pages.sort(
    key=lambda p: (
        p.name.lower() != "index.html",
        p.name.lower(),
    )
)


# Create XML sitemap.
urlset = Element(
    "urlset",
    {
        "xmlns":
            "http://www.sitemaps.org/schemas/sitemap/0.9"
    },
)


for page in pages:

    url = SubElement(
        urlset,
        "url",
    )

    # URL
    SubElement(
        url,
        "loc",
    ).text = url_for(page)

    # Last modification date
    SubElement(
        url,
        "lastmod",
    ).text = get_last_modified(
        page
    )

    # Change frequency
    SubElement(
        url,
        "changefreq",
    ).text = CHANGEFREQ.get(
        page.name,
        "weekly",
    )

    # Priority
    SubElement(
        url,
        "priority",
    ).text = PRIORITIES.get(
        page.name,
        "0.6",
    )


# Save sitemap.
output = ROOT / "sitemap.xml"

ElementTree(
    urlset
).write(
    output,
    encoding="utf-8",
    xml_declaration=True,
)


print("=" * 60)

print(
    "OPPORTUNITYBRIDGE SITEMAP GENERATOR"
)

print("=" * 60)

print(
    f"Generated sitemap.xml with {len(pages)} public HTML pages."
)

print(
    f"Output: {output}"
)

print("=" * 60)
