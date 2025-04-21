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

    def format_text(obj, include_specific=True):
        base = f"{obj['animal']} {obj['metier']}"
        if include_specific and obj.get("specificite"):
            base += f" for {obj['specificite']} {obj['animal']}"
        base += f" in {obj['ville']} {obj['quartier']}"
        return base[0].upper() + base[1:]

    def format_button(obj, index):
        label = format_text(obj, include_specific=(index < 2))
        json_data = json.dumps(obj).replace('"', '&quot;')  # Escape quotes for HTML attribute
        return f'<li><button data-obj="{json_data}">🔗 {label}</button></li>'

    buttons_html = '\n'.join([format_button(objects[i], i) for i in range(min(5, len(objects)))])

    html_content = markdown.markdown(md_content + f"\n\n{link_md}")

    return Markup(
        html_content +
        f"<h2>See also</h2>\n<ul>{buttons_html}</ul>"
    ) + Markup(
        f'''
        <script>
            document.querySelectorAll('button[data-obj]').forEach(button => {{
                button.addEventListener('click', async () => {{
                    const item = JSON.parse(button.getAttribute('data-obj'));
                    const base_url = "{base_url}";
                    try {{
                        const res = await fetch(base_url + 'generate-item', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ item }})
                        }});
                        const data = await res.json();
                        if (data.status !== 'success') {{
                            alert("Generation failed: " + (data.error || "Unknown error"));
                            return;
                        }}
                        window.open(data.url, '_blank');
                    }} catch (err) {{
                        console.error("Error:", err);
                        alert("An error occurred.");
                    }}
                }});
            }});
        </script>
        '''
    )
