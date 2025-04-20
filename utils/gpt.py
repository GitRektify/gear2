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

    # Replace placeholders with actual data
    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
