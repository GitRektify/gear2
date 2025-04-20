import os
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

    proptSimilarObject = "**\"Here is an original JSON object and a prompt template.\nPlease:\nGenerate 5 new JSON objects where each has only one key different from the original (changing one of ville, quartier, metier, animal, specificite).\n\"**"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    # Replace placeholders with actual data
    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
