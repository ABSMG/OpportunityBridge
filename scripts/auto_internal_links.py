from pathlib import Path
from html.parser import HTMLParser
import re

ROOT = Path(__file__).resolve().parents[1]

LINKS = {
    "scholarship": ("scholarships.html", "Scholarships"),
    "scholarships": ("scholarships.html", "Scholarships"),

    "job": ("jobs.html", "Jobs"),
    "jobs": ("jobs.html", "Jobs"),

    "internship": ("internships.html", "Internships"),
    "internships": ("internships.html", "Internships"),

    "course": ("courses.html", "Courses"),
    "courses": ("courses.html", "Courses"),

    "training": ("courses.html", "Courses"),

    "opportunity": ("opportunities.html", "Opportunities"),
    "opportunities": ("opportunities.html", "Opportunities"),

    "digital skills": ("digital-skills.html", "Digital Skills"),
    "career skills": ("career-skills.html", "Career Skills"),
}

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
    "contact.html",
}

MAX_CONTEXTUAL_LINKS = 5


class LinkParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.links = set()

        self.in_script = False
        self.in_style = False

        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        if tag == "script":
            self.in_script = True

        elif tag == "style":
            self.in_style = True

        if tag in {
            "script",
            "style",
            "nav",
            "footer",
        }:
            self.skip_depth += 1

        if tag == "a":

            for key, value in attrs:

                if (
                    key.lower() == "href"
                    and value
                ):

                    clean = (
                        value
                        .split("#")[0]
                        .split("?")[0]
                        .strip()
                    )

                    if clean:
                        self.links.add(clean)

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag == "script":
            self.in_script = False

        elif tag == "style":
            self.in_style = False

        if tag in {
            "script",
            "style",
            "nav",
            "footer",
        }:

            if self.skip_depth > 0:
                self.skip_depth -= 1


def get_existing_links(html):

    parser = LinkParser()

    parser.feed(html)

    return parser.links


def already_has_related_section(html):

    return (
        "related-opportunities"
        in html.lower()
    )


def detect_topics(html):

    text = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        html,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.lower()


def choose_links(html, current_page):

    existing_links = get_existing_links(
        html
    )

    text = detect_topics(html)

    selected = []

    # First choose links based on
    # actual article/page content.
    for keyword, (
        filename,
        label
    ) in LINKS.items():

        if filename == current_page:
            continue

        if filename in existing_links:
            continue

        if keyword not in text:
            continue

        if filename not in [
            item[0]
            for item in selected
        ]:

            selected.append(
                (
                    filename,
                    label
                )
            )

        if len(selected) >= MAX_CONTEXTUAL_LINKS:
            return selected

    # If the page does not contain enough
    # matching topics, add useful general
    # OpportunityBridge destinations.
    fallback = [
        (
            "opportunities.html",
            "Opportunities"
        ),
        (
            "scholarships.html",
            "Scholarships"
        ),
        (
            "jobs.html",
            "Jobs"
        ),
        (
            "internships.html",
            "Internships"
        ),
        (
            "courses.html",
            "Courses"
        ),
    ]

    for filename, label in fallback:

        if len(selected) >= MAX_CONTEXTUAL_LINKS:
            break

        if filename == current_page:
            continue

        if filename in existing_links:
            continue

        if filename in [
            item[0]
            for item in selected
        ]:
            continue

        selected.append(
            (
                filename,
                label
            )
        )

    return selected


def create_related_section(
    links
):

    if not links:
        return ""

    html = """
<section
  class="related-opportunities"
  aria-label="Related opportunities">

  <h2>Explore More Opportunities</h2>

  <p>
"""

    parts = []

    for filename, label in links:

        parts.append(
            f'    <a href="{filename}">{label}</a>'
        )

    html += "\n    | \n".join(
        parts
    )

    html += """

  </p>

</section>
"""

    return html


def insert_before_body(
    html,
    block
):

    match = re.search(
        r"</body\s*>",
        html,
        flags=re.I,
    )

    if not match:
        return html + block

    position = match.start()

    return (
        html[:position]
        + block
        + html[position:]
    )


def process_file(path):

    if path.name in EXCLUDED:
        return False

    if path.name.startswith("_"):
        return False

    try:

        html = path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        return False

    if already_has_related_section(
        html
    ):
        return False

    links = choose_links(
        html,
        path.name
    )

    if not links:
        return False

    block = create_related_section(
        links
    )

    updated = insert_before_body(
        html,
        block
    )

    if updated == html:
        return False

    path.write_text(
        updated,
        encoding="utf-8"
    )

    return True


def main():

    print("=" * 60)

    print(
        "OPPORTUNITYBRIDGE INTERNAL LINKING"
    )

    print("=" * 60)

    changed = []

    for path in sorted(
        ROOT.glob("*.html")
    ):

        if process_file(path):

            changed.append(
                path.name
            )

    if changed:

        print(
            "\nUpdated pages:"
        )

        for page in changed:

            print(
                f"- {page}"
            )

    else:

        print(
            "\nNo pages required new internal links."
        )

    print(
        f"\nPages updated: {len(changed)}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
