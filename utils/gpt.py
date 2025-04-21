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
    # openai_key = "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"
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=openai_key)  # Correct for openai>=1.0.0
    return client

def generate_content(data, prompt_config, internal_links):
    client = get_openai_client()
    objects = getRelativeInfo(client, data)

    prompt = prompt_config

    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content, objects

def getRelativeInfo(client, originJson):
    promptSimilarObject = (
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
        "### Input JSON:\n" + json.dumps(originJson, indent=2)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": promptSimilarObject}],
    )
    raw_data = response.choices[0].message.content

    similarStrings = re.findall(r'```json\s*(\{.*?\})\s*```', raw_data, re.DOTALL)
    
    newObjects = []
    for js in similarStrings:
        obj = json.loads(js)
        for key, value in obj.items():
            newObjects.append(value)

    for value in newObjects:
        print(f"key: {value}")

    return newObjects
