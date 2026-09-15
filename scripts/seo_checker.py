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

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()
        attrs = dict(attrs)

        if tag == "html":

            self.lang = (
                attrs.get("lang", "")
                or ""
            ).strip()

        elif tag == "title":

            self.in_title = True

        elif tag == "h1":

            self.h1_count += 1

        elif tag == "meta":

            name = (
                attrs.get("name", "")
                or ""
            ).lower().strip()

            property_name = (
                attrs.get("property", "")
                or ""
            ).lower().strip()

            content = (
                attrs.get("content", "")
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
                attrs.get("rel", "")
                or ""
            ).lower().strip()

            href = (
                attrs.get("href", "")
                or ""
            ).strip()

            if (
                rel == "canonical"
                and href
            ):
                self.canonical = href

    def handle_endtag(self, tag):

        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):

        if self.in_title:
            self.title += data


def valid_absolute_url(url):

    try:

        parsed = urlparse(url)

        return (
            parsed.scheme in {
                "http",
                "https"
            }
            and bool(parsed.netloc)
        )

    except Exception:

        return False


def is_generated_article(path):

    name = path.name.lower()

    # Automatically generated opportunity
    # articles use long descriptive slugs.
    generated_patterns = [
        "5-tips-for-",
        "bobcats-",
    ]

    return (
        any(
            name.startswith(pattern)
            for pattern in generated_patterns
        )
        or (
            len(name) > 55
            and name.endswith(".html")
        )
    )


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
        ], parser

    errors = []
    warnings = []

    title = parser.title.strip()

    # --------------------------------
    # REQUIRED SEO ELEMENTS
    # --------------------------------

    if not title:

        errors.append(
            "Missing <title>"
        )

    if not parser.meta_description:

        errors.append(
            "Missing meta description"
        )

    if parser.h1_count == 0:

        errors.append(
            "Missing <h1>"
        )

    elif parser.h1_count > 1:

        errors.append(
            f"Multiple <h1> tags ({parser.h1_count})"
        )

    if not parser.lang:

        errors.append(
            'Missing <html lang="">'
        )

    if not parser.canonical:

        errors.append(
            "Missing canonical URL"
        )

    elif not valid_absolute_url(
        parser.canonical
    ):

        errors.append(
            "Canonical is not an absolute URL"
        )

    elif not parser.canonical.startswith(
        BASE_URL
    ):

        errors.append(
            "Canonical points outside OpportunityBridge"
        )

    # --------------------------------
    # TITLE LENGTH = WARNING ONLY
    # --------------------------------

    if title:

        if len(title) > 65:

            warnings.append(
                f"Title is long ({len(title)} characters)"
            )

        elif len(title) < 20:

            warnings.append(
                f"Title is short ({len(title)} characters)"
            )

    # --------------------------------
    # OPTIONAL SEO ELEMENTS
    # --------------------------------

    if not parser.meta_robots:

        warnings.append(
            "Missing robots meta tag"
        )

    if not parser.og_title:

        warnings.append(
            "Missing og:title"
        )

    if not parser.og_description:

        warnings.append(
            "Missing og:description"
        )

    return errors, warnings, parser


def is_google_verification(path):

    return (
        path.name.startswith("google")
        and path.name.endswith(".html")
    )


def main():

    print("=" * 70)

    print(
        "OPPORTUNITYBRIDGE SEO CHECK"
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

    total_errors = 0
    total_warnings = 0
    pages_with_errors = 0

    titles = {}
    canonicals = {}

    for page in pages:

        result = check_page(page)

        errors, warnings, parser = result

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

        if errors:

            pages_with_errors += 1
            total_errors += len(errors)

            print(
                f"\n❌ {page.name}"
            )

            for error in errors:

                print(
                    f"   ERROR: {error}"
                )

        else:

            print(
                f"✅ {page.name}"
            )

        for warning in warnings:

            total_warnings += 1

            print(
                f"   ⚠️ WARNING: {warning}"
            )

    # --------------------------------
    # DUPLICATE TITLES
    # --------------------------------

    for title, page_list in titles.items():

        if len(page_list) > 1:

            total_errors += 1

            print(
                "\n❌ DUPLICATE TITLE"
            )

            print(
                f"   Pages: {page_list}"
            )

    # --------------------------------
    # DUPLICATE CANONICALS
    # --------------------------------

    for canonical, page_list in canonicals.items():

        if len(page_list) > 1:

            total_errors += 1

            print(
                "\n❌ DUPLICATE CANONICAL"
            )

            print(
                f"   Canonical: {canonical}"
            )

            print(
                f"   Pages: {page_list}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        f"Pages checked: {len(pages)}"
    )

    print(
        f"Pages with errors: {pages_with_errors}"
    )

    print(
        f"Total errors: {total_errors}"
    )

    print(
        f"SEO warnings: {total_warnings}"
    )

    print(
        "=" * 70
    )

    if total_errors:

        print(
            "SEO CHECK FAILED."
        )

        raise SystemExit(1)

    print(
        "SEO CHECK PASSED."
    )

    if total_warnings:

        print(
            "Warnings detected, but they do not block deployment."
        )


if __name__ == "__main__":
    main()
