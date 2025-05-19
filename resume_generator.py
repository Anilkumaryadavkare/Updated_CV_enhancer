from pathlib import Path
from markdown2 import markdown  # pip install markdown2
from jinja2 import Environment, FileSystemLoader
import weasyprint, logging

logging.basicConfig(level=logging.ERROR)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"

def html_from_content(raw_text: str, template_id: str) -> str:
    """
    Convert the *raw resume text* (plain‑text / simple markdown) into styled HTML.
    Renders the text using the given template (e.g., 'clean-blue', 'modern-sleek').
    """
    raw_text = (raw_text or "").strip()
    if not raw_text:
        raise ValueError("Empty resume content")

    # 1. markdown → HTML  (bold, lists, tables, etc.)
    html_resume = markdown(raw_text, extras=["fenced-code-blocks", "tables"])

    # 2. inject into chosen HTML template
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(f"{template_id}.html")
    return template.render(content=html_resume)

def pdf_bytes(raw_text: str, template_id: str = "clean-blue") -> bytes:
    """
    Return finished PDF bytes for sending back to the client.

    `template_id` can be:
    - "clean-blue" (default)
    - "modern-sleek" (for a modern, ATS-safe look)
    """
    html = html_from_content(raw_text, template_id)
    return weasyprint.HTML(string=html).write_pdf(
        stylesheets=[
            weasyprint.CSS(string="@page { size:A4; margin:1cm }")
        ]
    )
