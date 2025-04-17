import markdown
from markupsafe import Markup
import json

# Load cities.json only once (globally)
with open("cities.json", encoding="utf-8") as f:
    city_data = json.load(f)

# Create a fast lookup dictionary: ville -> {lat, lng}
city_lookup = {
    entry["ville"]: {
        "lat": entry["lat"],
        "lng": entry["lng"]
    }
    for entry in city_data
}

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

    # Get lat/lng from lookup (default to 0.0 if city not found)
    location = city_lookup.get(city, {"lat": 0.0, "lng": 0.0})
    lat = location["lat"]
    lng = location["lng"]

    # Build link text and URL
    link_text = f"{verb} {pro_display} à {city}"
    link_url = f"https://planipets.com/etablissements?name={pro}&address={city}%2C%20France&lat={lat}&lng={lng}"

    # Markdown link
    link_md = f"[{link_text}]({link_url})"

    # Convert to HTML
    return Markup(markdown.markdown(md_content + f"\n\n{link_md}"))
