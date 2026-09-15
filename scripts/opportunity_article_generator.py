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
        OUTPUT_DIR /
        f"{slug}.html"
    ).exists()


def create_article(item):

    title = item.get(
        "title",
        "New Opportunity"
    ).strip()

    publisher_name = item.get(
        "publisher_name",
        ""
    ).strip()

    publisher_url = item.get(
        "publisher_url",
        ""
    ).strip()

    source_url = item.get(
        "source_url",
        ""
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
        keywords[:8]
    )

    safe_title = escape(title)
    safe_publisher = escape(
        publisher_name or "Verified source"
    )
    safe_url = escape(
        publisher_url or source_url
    )
    safe_keywords = escape(
        keyword_text
    )

    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    filename = f"{slug}.html"

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>

  <meta charset="UTF-8">

  <meta name="viewport"
        content="width=device-width, initial-scale=1.0">

  <title>{safe_title} | OpportunityBridge</title>

  <meta name="description"
        content="Learn about {safe_title}, eligibility information, opportunity details and the verified source.">

  <meta name="keywords"
        content="{safe_keywords}, Tanzania, Africa, scholarships, jobs, internships, courses">

  <meta name="robots"
        content="index, follow">

  <link rel="canonical"
        href="https://absmg.github.io/{filename}">

  <meta property="og:title"
        content="{safe_title} | OpportunityBridge">

  <meta property="og:description"
        content="Explore this opportunity and verify the latest information from the listed source.">

  <meta property="og:type"
        content="article">

  <meta property="og:url"
        content="https://absmg.github.io/{filename}">

</head>

<body>

<header>

  <nav aria-label="Main navigation">

    <a href="index.html">
      OpportunityBridge
    </a>

    |
    <a href="scholarships.html">
      Scholarships
    </a>

    |
    <a href="jobs.html">
      Jobs
    </a>

    |
    <a href="internships.html">
      Internships
    </a>

    |
    <a href="courses.html">
      Courses
    </a>

    |
    <a href="opportunities.html">
      Opportunities
    </a>

  </nav>

  <h1>{safe_title}</h1>

</header>


<main>

  <article>

    <p>
      <strong>OpportunityBridge</strong>
      discovered this opportunity through its
      automated opportunity discovery system.
    </p>


    <h2>Opportunity Overview</h2>

    <p>
      This page summarizes the opportunity information
      identified by OpportunityBridge. Requirements,
      eligibility, application dates and availability
      may change, so applicants should verify all details
      directly with the source before applying.
    </p>


    <h2>Opportunity Type</h2>

    <p>
      {safe_keywords}
    </p>


    <h2>Source</h2>

    <p>
      Publisher:
      <strong>{safe_publisher}</strong>
    </p>

    <p>
      <a
        href="{safe_url}"
        target="_blank"
        rel="noopener noreferrer nofollow">
        Visit the source and verify this opportunity
      </a>
    </p>


    <h2>Before You Apply</h2>

    <ul>

      <li>
        Confirm the application deadline.
      </li>

      <li>
        Check the eligibility requirements.
      </li>

      <li>
        Confirm whether the opportunity is open
        to Tanzanian or international applicants.
      </li>

      <li>
        Use the publisher's official information
        before submitting personal documents.
      </li>

    </ul>


    <h2>Important Notice</h2>

    <p>
      OpportunityBridge does not guarantee admission,
      employment, funding or selection.
      Information may change after publication.
      Always verify the opportunity directly with
      the publisher before applying.
    </p>


    <p>
      <strong>Last checked:</strong>
      {today}
    </p>

  </article>


  <hr>


  <section
    aria-label="Explore more opportunities">

    <h2>Explore More Opportunities</h2>

    <p>

      <a href="scholarships.html">
        Scholarships
      </a>
      |

      <a href="jobs.html">
        Jobs
      </a>
      |

      <a href="internships.html">
        Internships
      </a>
      |

      <a href="courses.html">
        Courses
      </a>
      |

      <a href="opportunities.html">
        All Opportunities
      </a>

    </p>

  </section>


</main>


<footer>

  <p>
    <a href="about.html">
      About OpportunityBridge
    </a>
    |
    <a href="contact.html">
      Contact
    </a>
    |
    <a href="privacy.html">
      Privacy
    </a>
    |
    <a href="disclaimer.html">
      Disclaimer
    </a>
  </p>

  <p>
    © OpportunityBridge
  </p>

</footer>

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
    print(
        "OPPORTUNITYBRIDGE ARTICLE GENERATOR"
    )
    print("=" * 60)

    if not INPUT.exists():

        raise SystemExit(
            "ERROR: approved_opportunities.json not found."
        )

    data = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    items = data.get(
        "approved_items",
        []
    )

    generated = []

    for item in items:

        filename = create_article(
            item
        )

        if filename:

            generated.append(
                filename
            )

    print(
        f"Approved opportunities: {len(items)}"
    )

    print(
        f"New articles generated: {len(generated)}"
    )

    if generated:

        print("\nGenerated articles:")

        for filename in generated:

            print(
                f"- {filename}"
            )

    else:

        print(
            "No new articles required."
        )

    print("=" * 60)


if __name__ == "__main__":
    main()
