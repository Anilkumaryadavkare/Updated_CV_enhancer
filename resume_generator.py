from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import weasyprint
import logging
import json
from collections import defaultdict

logging.basicConfig(level=logging.ERROR)


def html_from_content(structured_resume: str, template_id: str) -> str:
    """
    Turn the JSON payload coming from the FastAPI endpoint into HTML.
    - contact stays a list (joined by <br> in the template)
    - summary becomes a plain paragraph
    - experience / skills / education:
        * each list item is joined
        * if any of those items already starts with <li>…</li>, wrap the whole block in <ul>…</ul>
    """
    try:
        if not structured_resume.strip():
            raise ValueError("Empty resume content")

        # 1. Parse JSON -----------------------------------------------------
        try:
            resume_data = json.loads(structured_resume)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}") from e

        # 2. Extract / normalise sections ----------------------------------
        sections = resume_data.get("sections", {})
        if isinstance(sections, defaultdict):
            sections = dict(sections)

        processed = {}
        for key, value in sections.items():
            # Convert defaultdicts-in-values, if any
            if isinstance(value, defaultdict):
                value = dict(value)

            # ── CONTACT (list) ────────────────────────────────────────────
            if key == "contact":
                processed[key] = [str(item).strip() for item in value]

            # ── SUMMARY (list ➜ single paragraph) ─────────────────────────
            elif key == "summary":
                if isinstance(value, list):
                    processed[key] = " ".join(str(item).strip() for item in value)
                else:
                    processed[key] = str(value)

            # ── EXPERIENCE / SKILLS / EDUCATION ───────────────────────────
            else:
                if isinstance(value, list):
                    items = [str(item) for item in value]
                    block = "\n".join(items)

                    # if list contains <li> … wrap once in <ul>
                    if any(item.lstrip().startswith("<li") for item in items):
                        block = f"<ul>\n{block}\n</ul>"

                    processed[key] = block
                else:
                    processed[key] = str(value)

        # 3. Render with Jinja2 --------------------------------------------
        base_dir = Path(__file__).parent / "templates"
        env = Environment(loader=FileSystemLoader(base_dir))
        template = env.get_template(f"{template_id}.html")
        return template.render(sections=processed)

    except Exception as e:
        logging.error(f"Template error: {str(e)}")
        raise


def pdf_bytes(content: str, template_id: str) -> bytes:
    """Generate PDF bytes via WeasyPrint."""
    try:
        html = html_from_content(content, template_id)
        return weasyprint.HTML(string=html).write_pdf(
            stylesheets=[weasyprint.CSS(string="@page { size: A4; margin: 1cm; }")]
        )
    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        raise
