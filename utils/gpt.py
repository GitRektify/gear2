import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load .env only in local dev
if os.getenv("RAILWAY_ENV") is None:
    load_dotenv()

def get_openai_client():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=openai_key)

def generate_content(data, prompt_config, internal_links):
    client = get_openai_client()
    objects = get_relative_info(client, data)

    # Replace all {{key}} in the prompt template
    for key in data:
        prompt_config = prompt_config.replace(f"{{{{{key}}}}}", data[key])

    prompt_config = prompt_config.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_config}],
    )

    return response.choices[0].message.content, objects

def get_relative_info(client, origin_json):
    prompt_similar_object = (
        "**Prompt Message to ChatGPT:**\n"
        "Here is an original JSON object and some link generation rules.  \n"
        "Please generate **5 new JSON objects** for 5 internal links:  \n"
        "### Rules:\n"
        "🔷 **Block 1 – Same service + same city**  \n"
        "- `link_1_spec_same`: Same service + same city + same specificity (different page)  \n"
        "- `link_2_spec_same`: Another one like above  \n"
        "- `link_3_no_spec`: Same service + same city, **without specificity**\n"
        "🔷 **Block 2 – Cross-services (same city)**  \n"
        "- `link_4_cross`: Related service (educateur veterinaire comportementaliste)  \n"
        "- `link_5_cross`: Another different related service  \n"
        "💡 If a slot can't be filled (e.g. no relevant variation), leave it blank (no error).  \n"
        "✅ Respond with 5 separate JSON objects, clearly labeled per link.\n"
        "### Input JSON:\n" + json.dumps(origin_json, indent=2)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_similar_object}],
    )

    raw_data = response.choices[0].message.content

    # Extract all code blocks containing JSON
    similar_strings = re.findall(r'```json\s*(\{.*?\})\s*```', raw_data, re.DOTALL)
    new_objects = []

    for js in similar_strings:
        obj = json.loads(js)
        for _, value in obj.items():
            new_objects.append(value)
            print(f"Generated variation: {value}")

    return new_objects
