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

def md_to_html(md_content, city, pro, objects, base_url):
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

    # Profession-to-verb mapping
    verb_map = {
        "toiletteur": "Réserver un",
        "éducateur": "Contacter un",
        "ostéopathe": "Trouver un"
    }

    pro_clean = pro.lower()
    verb = verb_map.get(pro_clean, "Contacter un")
    pro_display = pro.capitalize()

    location = city_lookup.get(city, {"lat": 0.0, "lng": 0.0})
    lat = location["lat"]
    lng = location["lng"]

    link_text = f"{verb} {pro_display} à {city}"
    link_url = f"https://planipets.com/etablissements?name={pro}&address={city}%2C%20France&lat={lat}&lng={lng}"
    link_md = f"[{link_text}]({link_url})"

    # Format button text
    def format_text(obj, include_specific=True):
        base = f"{obj['animal']} {obj['metier']}"
        if include_specific and obj.get("specificite"):
            base += f" for {obj['specificite']} {obj['animal']}"
        base += f" in {obj['ville']} {obj['quartier']}"
        return base[0].upper() + base[1:]

    # Generate raw HTML buttons
    def format_button(obj, index):
        label = format_text(obj, include_specific=(index < 2))
        json_obj = json.dumps(obj).replace('"', '&quot;')  # Escape for HTML
        print("HHHHHHHHHHHHHHHH", json_obj)
        return f'<li><button onclick="generateAndOpen({json_obj}, {base_url})">🔗 {label}</button></li>'

    buttons_html = '\n'.join([format_button(objects[i], i) for i in range(5)])

    # Markdown only for md_content and link
    html_content = markdown.markdown(md_content + f"\n\n{link_md}")

    # Return combined HTML with raw HTML buttons and JS
    return Markup(
        html_content +
        f"<h2>See also</h2>\n<ul>{buttons_html}</ul>"
    ) + Markup(
        '''<script>
            async function generateAndOpen(item, base_url) {
                console.log('base_url');
                try {
                    const generateRes = await fetch(base_url + '/generate-item', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ item })
                    });
                    const genData = await generateRes.json();
                    if (genData.status !== 'success') {
                        alert("Generation failed: " + (genData.error || "Unknown error"));
                        return;
                    }
                    window.open(genData.url, '_blank');
                } catch (err) {
                    console.error("Error:", err);
                    alert("An error occurred.");
                }
            }
        </script>'''
    )

