import markdown
from markupsafe import Markup

def md_to_html(md_content):
    return Markup(markdown.markdown(md_content))