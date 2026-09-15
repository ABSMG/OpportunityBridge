from pathlib import Path
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, ElementTree
import subprocess

BASE_URL = "https://absmg.github.io"
ROOT = Path(__file__).resolve().parents[1]

EXCLUDED = {
    "404.html",
    "login.html",
    "logout.html",
    "register.html",
    "dashboard.html",
}

PRIORITIES = {
    "index.html": "1.0",
    "scholarships.html": "0.9",
    "jobs.html": "0.9",
    "internships.html": "0.9",
    "courses.html": "0.9",
    "opportunities.html": "0.9",
    "skills.html": "0.8",
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
                str(path.relative_to(ROOT))
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
        tz=timezone.utc
    ).date().isoformat()


def url_for(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()

    if relative == "index.html":
        return BASE_URL + "/"

    return BASE_URL + "/" + relative


pages = []

for path in ROOT.glob("*.html"):

    if path.name in EXCLUDED:
        continue

    if path.name.startswith("_"):
        continue

    pages.append(path)


pages.sort(
    key=lambda p: (
        p.name.lower() != "index.html",
        p.name.lower()
    )
)


urlset = Element(
    "urlset",
    {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }
)


for page in pages:

    url = SubElement(urlset, "url")

    SubElement(url, "loc").text = url_for(page)

    SubElement(
        url,
        "lastmod"
    ).text = get_last_modified(page)

    SubElement(
        url,
        "priority"
    ).text = PRIORITIES.get(
        page.name,
        "0.6"
    )


output = ROOT / "sitemap.xml"

ElementTree(urlset).write(
    output,
    encoding="utf-8",
    xml_declaration=True
)


print(
    f"Generated sitemap.xml with {len(pages)} public HTML pages."
)
