from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

# Pages we want to promote through internal links.
LINKS = {
    "scholarships": "scholarships.html",
    "jobs": "jobs.html",
    "internships": "internships.html",
    "courses": "courses.html",
    "opportunities": "opportunities.html",
    "digital skills": "digital-skills.html",
    "career skills": "career-skills.html",
}

EXCLUDED = {
    "404.html",
    "login.html",
    "logout.html",
    "register.html",
    "dashboard.html",
    "privacy.html",
    "disclaimer.html",
    "contact.html",
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True

        if tag == "a":
            for key, value in attrs:
                if key == "href" and value:
                    self.links.add(value.split("#")[0].split("?")[0])

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False


def get_existing_links(html):
    parser = LinkParser()
    parser.feed(html)
    return parser.links


def add_internal_links(html, current_page):
    existing_links = get_existing_links(html)

    suggestions = []

    for keyword, filename in LINKS.items():

        if filename == current_page:
            continue

        if filename in existing_links:
            continue

        suggestions.append(
            f'<a href="{filename}">{keyword.title()}</a>'
        )

    if not suggestions:
        return html

    block = """
<section class="related-opportunities" aria-label="Related resources">
  <h2>Explore More Opportunities</h2>
  <p>
    """
    
    block += " | ".join(suggestions)

    block += """
  </p>
</section>
"""

    # Insert before </body> when possible.
    if "</body>" in html.lower():
        position = html.lower().rfind("</body>")
        return html[:position] + block + html[position:]

    return html + block


def process_file(path):
    if path.name in EXCLUDED:
        return False

    if path.name.startswith("_"):
        return False

    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    updated = add_internal_links(html, path.name)

    if updated == html:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main():
    changed = []

    for path in ROOT.glob("*.html"):
        if process_file(path):
            changed.append(path.name)

    print("Internal linking scan complete.")

    if changed:
        print("Updated pages:")
        for page in changed:
            print(f"- {page}")
    else:
        print("No pages required new internal links.")


if __name__ == "__main__":
    main()
