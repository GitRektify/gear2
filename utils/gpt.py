import os
from openai import OpenAI
from dotenv import load_dotenv

def get_openai_client():
    load_dotenv()  # only affects local development

    openai_key = os.environ.get("OPENAI_API_KEY")
    print(openai_key)
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=openai_key)

def generate_content(data, prompt_config, internal_links):
    client = get_openai_client()  # <- client is initialized here
    prompt = prompt_config

    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
