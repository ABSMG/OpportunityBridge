from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED = {
    "404.html",
    "login.html",
    "logout.html",
    "register.html",
    "dashboard.html",
    "privacy.html",
    "disclaimer.html",
}


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.h1_count = 0
        self.lang = None
        self.meta_description = False
        self.canonical = False
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "html":
            self.lang = attrs.get("lang")

        elif tag == "title":
            self.in_title = True

        elif tag == "h1":
            self.h1_count += 1

        elif tag == "meta":
            if attrs.get("name", "").lower() == "description":
                if attrs.get("content", "").strip():
                    self.meta_description = True

        elif tag == "link":
            if attrs.get("rel", "").lower() == "canonical":
                if attrs.get("href", "").strip():
                    self.canonical = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()


def check_page(path):
    parser = SEOParser()

    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except Exception as error:
        return [f"READ ERROR: {error}"]

    issues = []

    if not parser.title.strip():
        issues.append("Missing <title>")

    if not parser.meta_description:
        issues.append("Missing meta description")

    if parser.h1_count == 0:
        issues.append("Missing <h1>")
    elif parser.h1_count > 1:
        issues.append(f"Multiple <h1> tags ({parser.h1_count})")

    if not parser.lang:
        issues.append('Missing <html lang="">')

    if not parser.canonical:
        issues.append("Missing canonical URL")

    return issues


def is_google_verification(path):
    return (
        path.name.startswith("google")
        and path.name.endswith(".html")
    )


def main():
    pages = []

    for path in sorted(ROOT.glob("*.html")):
        if path.name in EXCLUDED:
            continue

        if path.name.startswith("_"):
            continue

        if is_google_verification(path):
            continue

        pages.append(path)

    total_issues = 0
    pages_with_issues = 0

    print("=" * 60)
    print("OPPORTUNITYBRIDGE SEO CHECK")
    print("=" * 60)

    for page in pages:
        issues = check_page(page)

        if issues:
            pages_with_issues += 1
            total_issues += len(issues)

            print(f"\n❌ {page.name}")

            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ {page.name}")

    print("\n" + "=" * 60)
    print(f"Pages checked: {len(pages)}")
    print(f"Pages with issues: {pages_with_issues}")
    print(f"Total issues: {total_issues}")
    print("=" * 60)

    if total_issues:
        raise SystemExit(1)

    print("SEO CHECK PASSED.")


if __name__ == "__main__":
    main()
