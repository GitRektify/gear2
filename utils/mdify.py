import markdown
from markupsafe import Markup

def md_to_html(md_content, city, pro):
    # Define profession-to-verb mapping
    verb_map = {
        "toiletteur": "Réserver un",
        "éducateur": "Contacter un",
        "ostéopathe": "Trouver un"
    }

    # Normalize the profession to lowercase (if needed)
    pro_clean = pro.lower()

    # Get the verb prefix or default
    verb = verb_map.get(pro_clean, "Contacter un")

    # Capitalize profession for display
    pro_display = pro.capitalize()

    # Build link text and URL
    link_text = f"{verb} {pro_display} à {city}"
    link_url = f"https://planipets.com/etablissements?name={pro}&address={city}"

    # Markdown link
    link_md = f"[{link_text}]({link_url})"

    # Convert to HTML
    return Markup(markdown.markdown(md_content + f"\n\n{link_md}"))
