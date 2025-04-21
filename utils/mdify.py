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

def md_to_html(md_content, city, pro, objects):
    import json

    # If any object is a string (not a dict), convert the whole list
    if isinstance(objects[0], str):
        valid_objects = []
        for i, obj in enumerate(objects):
            if obj.strip():
                try:
                    valid_objects.append(json.loads(obj))
                except json.JSONDecodeError:
                    print(f"Warning: Object at index {i} is not valid JSON:\n{obj}")
            else:
                print(f"Warning: Object at index {i} is empty.")
        objects = valid_objects

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

    # Create text links from generated objects
    def format_text(obj, include_specific=True):
        base = f"{obj['animal']} {obj['metier']}"
        if include_specific and obj.get("specificite"):
            base += f" for {obj['specificite']} {obj['animal']}"
        base += f" in {obj['ville']} {obj['quartier']}"
        return base[0].upper() + base[1:]

    link_one_text = format_text(objects[0])
    link_two_text = format_text(objects[1])
    link_thr_text = format_text(objects[2], include_specific=False)
    link_for_text = format_text(objects[3], include_specific=False)
    link_fiv_text = format_text(objects[4], include_specific=False)

    # (Optional) Log for debugging
    print("Link 1:", link_one_text)
    print("Link 2:", link_two_text)
    print("Link 3:", link_thr_text)
    print("Link 4:", link_for_text)
    print("Link 5:", link_fiv_text)

    # Convert to HTML with additional links if needed
    return Markup(markdown.markdown(
        md_content
        + f"\n\n{link_md}"
        + f"<h2>See also</h2>"
        + f"\n\n- {link_one_text}"
        + f"\n- {link_two_text}"
        + f"\n- {link_thr_text}"
        + f"\n- {link_for_text}"
        + f"\n- {link_fiv_text}"
    ))
