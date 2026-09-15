from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import re

ROOT = Path(__file__).resolve().parents[1]

BASE_URL = "https://absmg.github.io"

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

class SEOParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.title = ""
        self.h1_count = 0
        self.lang = None

        self.meta_description = False
        self.meta_robots = False

        self.og_title = False
        self.og_description = False

        self.canonical = ""

        self.in_title = False

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        attrs = dict(attrs)

        tag = tag.lower()

        if tag == "html":

            self.lang = (
                attrs.get("lang")
                or ""
            ).strip()

        elif tag == "title":

            self.in_title = True

        elif tag == "h1":

            self.h1_count += 1

        elif tag == "meta":

            name = (
                attrs.get(
                    "name",
                    ""
                )
                .lower()
                .strip()
            )

            property_name = (
                attrs.get(
                    "property",
                    ""
                )
                .lower()
                .strip()
            )

            content = (
                attrs.get(
                    "content",
                    ""
                )
                or ""
            ).strip()

            if (
                name == "description"
                and content
            ):

                self.meta_description = True

            if (
                name == "robots"
                and content
            ):

                self.meta_robots = True

            if (
                property_name == "og:title"
                and content
            ):

                self.og_title = True

            if (
                property_name == "og:description"
                and content
            ):

                self.og_description = True

        elif tag == "link":

            rel = (
                attrs.get(
                    "rel",
                    ""
                )
                .lower()
                .strip()
            )

            href = (
                attrs.get(
                    "href",
                    ""
                )
                or ""
            ).strip()

            if (
                rel == "canonical"
                and href
            ):

                self.canonical = href

    def handle_endtag(
        self,
        tag
    ):

        if tag.lower() == "title":

            self.in_title = False

    def handle_data(
        self,
        data
    ):

        if self.in_title:

            self.title += data


def valid_absolute_url(url):

    try:

        parsed = urlparse(
            url
        )

        return (
            parsed.scheme
            in {"http", "https"}
            and bool(
                parsed.netloc
            )
        )

    except Exception:

        return False


def check_page(path):

    parser = SEOParser()

    try:

        parser.feed(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as error:

        return [
            f"READ ERROR: {error}"
        ]

    issues = []

    title = (
        parser.title
        .strip()
    )

    if not title:

        issues.append(
            "Missing <title>"
        )

    elif len(title) < 20:

        issues.append(
            "Title is too short"
        )

    elif len(title) > 65:

        issues.append(
            "Title is longer than recommended"
        )

    if not parser.meta_description:

        issues.append(
            "Missing meta description"
        )

    if parser.h1_count == 0:

        issues.append(
            "Missing <h1>"
        )

    elif parser.h1_count > 1:

        issues.append(
            f"Multiple <h1> tags ({parser.h1_count})"
        )

    if not parser.lang:

        issues.append(
            'Missing <html lang="">'
        )

    if not parser.canonical:

        issues.append(
            "Missing canonical URL"
        )

    else:

        if not valid_absolute_url(
            parser.canonical
        ):

            issues.append(
                "Canonical is not an absolute URL"
            )

        elif not parser.canonical.startswith(
            BASE_URL
        ):

            issues.append(
                "Canonical points outside OpportunityBridge"
            )

    if not parser.meta_robots:

        issues.append(
            "Missing robots meta tag"
        )

    if not parser.og_title:

        issues.append(
            "Missing og:title"
        )

    if not parser.og_description:

        issues.append(
            "Missing og:description"
        )

    return issues, parser


def is_google_verification(path):

    return (
        path.name.startswith("google")
        and path.name.endswith(".html")
    )


def main():

    print("=" * 70)

    print(
        "OPPORTUNITYBRIDGE FINAL SEO CHECK"
    )

    print("=" * 70)

    pages = []

    for path in sorted(
        ROOT.glob("*.html")
    ):

        if path.name in EXCLUDED:
            continue

        if path.name.startswith("_"):
            continue

        if is_google_verification(path):
            continue

        pages.append(path)

    total_issues = 0
    pages_with_issues = 0

    titles = {}
    canonicals = {}

    for page in pages:

        issues, parser = check_page(
            page
        )

        title = (
            parser.title
            .strip()
            .lower()
        )

        canonical = (
            parser.canonical
            .strip()
            .lower()
        )

        if title:

            titles.setdefault(
                title,
                []
            ).append(
                page.name
            )

        if canonical:

            canonicals.setdefault(
                canonical,
                []
            ).append(
                page.name
            )

        if issues:

            pages_with_issues += 1

            total_issues += len(
                issues
            )

            print(
                f"\n❌ {page.name}"
            )

            for issue in issues:

                print(
                    f"   - {issue}"
                )

        else:

            print(
                f"✅ {page.name}"
            )

    # Duplicate title detection
    for title, pages_list in titles.items():

        if len(pages_list) > 1:

            total_issues += 1

            print(
                "\n❌ DUPLICATE TITLE"
            )

            print(
                f"   {pages_list}"
            )

    # Duplicate canonical detection
    for canonical, pages_list in canonicals.items():

        if len(pages_list) > 1:

            total_issues += 1

            print(
                "\n❌ DUPLICATE CANONICAL"
            )

            print(
                f"   {canonical}"
            )

            print(
                f"   Pages: {pages_list}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        f"Pages checked: {len(pages)}"
    )

    print(
        f"Pages with issues: {pages_with_issues}"
    )

    print(
        f"Total issues: {total_issues}"
    )

    print(
        "=" * 70
    )

    if total_issues:

        raise SystemExit(
            1
        )

    print(
        "SEO CHECK PASSED."
    )


if __name__ == "__main__":

    main()
