from pathlib import Path
from datetime import datetime, timezone
import json
import re
import html


ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "approved_opportunities.json"
OUTPUT_DIR = ROOT


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)

    return text[:80].strip("-")


def escape(value):
    return html.escape(
        str(value or "").strip()
    )


def article_exists(slug):
    return (
        OUTPUT_DIR / f"{slug}.html"
    ).exists()


def create_article(item):
    title = item.get(
        "title",
        "New Opportunity"
    ).strip()

    source_url = item.get(
        "source_url",
        ""
    ).strip()

    source_name = item.get(
        "source",
        "Official source"
    ).strip()

    keywords = item.get(
        "matched_keywords",
        []
    )

    slug = slugify(title)

    if not slug:
        return None

    if article_exists(slug):
        return None

    keyword_text = ", ".join(
        keywords[:6]
    )

    safe_title = escape(title)
    safe_source = escape(source_name)
    safe_url = escape(source_url)
    safe_keywords = escape(keyword_text)

    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    filename = f"{slug}.html"

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>{safe_title} | OpportunityBridge</title>

  <meta
    name="description"
    content="Learn about {safe_title}, including the available opportunity information and official source."
  >

  <meta
    name="keywords"
    content="{safe_keywords}, Tanzania, Africa, OpportunityBridge"
  >

  <link
    rel="canonical"
    href="https://absmg.github.io/{filename}"
  >
</head>

<body>

<header>
  <h1>{safe_title}</h1>
</header>

<main>

  <p>
    <strong>OpportunityBridge</strong> has identified this
    opportunity as a potential scholarship, job, internship,
    course, training, fellowship or related opportunity.
  </p>

  <h2>Opportunity Overview</h2>

  <p>
    This page provides the available information discovered
    from the listed source. Applicants should always confirm
    the latest requirements, eligibility conditions and
    deadlines directly with the official source before applying.
  </p>

  <h2>Opportunity Type</h2>

  <p>
    {safe_keywords}
  </p>

  <h2>Source</h2>

  <p>
    Source identified as:
    <strong>{safe_source}</strong>
  </p>

  <p>
    <a
      href="{safe_url}"
      target="_blank"
      rel="noopener noreferrer"
    >
      Visit the source and verify the opportunity
    </a>
  </p>

  <h2>Important Notice</h2>

  <p>
    OpportunityBridge does not guarantee admission,
    employment, funding or selection. Information may change
    after publication. Always verify the opportunity directly
    with the official source before submitting an application
    or personal information.
  </p>

  <p>
    <strong>Last checked:</strong> {today}
  </p>

  <hr>

  <p>
    <a href="index.html">Home</a> |
    <a href="scholarships.html">Scholarships</a> |
    <a href="jobs.html">Jobs</a> |
    <a href="internships.html">Internships</a> |
    <a href="courses.html">Courses</a> |
    <a href="opportunities.html">Opportunities</a>
  </p>

</main>

</body>
</html>
"""

    path = OUTPUT_DIR / filename

    path.write_text(
        content,
        encoding="utf-8"
    )

    return filename


def main():
    print("=" * 60)
    print("OPPORTUNITYBRIDGE ARTICLE GENERATOR")
    print("=" * 60)

    if not INPUT.exists():
        raise SystemExit(
            "ERROR: approved_opportunities.json was not found."
        )

    data = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    approved = data.get(
        "approved_items",
        []
    )

    created = []

    for item in approved:
        filename = create_article(item)

        if filename:
            created.append(filename)

    print(f"Approved opportunities: {len(approved)}")
    print(f"New articles created: {len(created)}")

    if created:
        print("\nCreated articles:")

        for filename in created:
            print(f"- {filename}")

    print("=" * 60)


if __name__ == "__main__":
    main()
