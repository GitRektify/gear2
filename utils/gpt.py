import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load .env only in local dev
if os.getenv("RAILWAY_ENV") is None:
    load_dotenv()

def get_openai_client():
    openai_key = "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"
    # openai_key = os.environ.get("OPENAI_API_KEY")

    print(f"🔑 OpenAI Key: {openai_key}")

    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=openai_key)

def generate_content(data, prompt_config, internal_links):
    client = get_openai_client()

    prompt = prompt_config

    promptSimilarObject = "**Prompt Message to ChatGPT:**\nHere is an original JSON object and some link generation rules.  \nPlease generate **5 new JSON objects** for 5 internal links:  \n### Rules:\n🔷 **Block 1 – Same service + same city**  \n- `link_1_spec_same`: Same service + same city + same specificity (different page)  \n- `link_2_spec_same`: Another one like above  \n- `link_3_no_spec`: Same service + same city, **without specificity**\n🔷 **Block 2 – Cross-services (same city)**  \n- `link_4_cross`: Related service (educateur veterinaire comportementaliste)  \n- `link_5_cross`: Another different related service  \n💡 If a slot can't be filled (e.g. no relevant variation), leave it blank (no error).  \n✅ Respond with 5 separate JSON objects, clearly labeled per link.\n### Input JSON:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": promptSimilarObject + str(data)}],
    )
    raw_data = response.choices[0].message.content
    similarStrings = re.findall(r'```json\s*(\{.*?\})\s*```', raw_data, re.DOTALL)
    # Convert them into Python dictionaries
    similarObjects = [json.loads(js) for js in similarStrings]

    # Print or use the objects
    for i, obj in enumerate(similarObjects, 1):
        print(f"Object {i}: {obj}")
    sdfsd=0

    # Replace placeholders with actual data
    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
