import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_key = os.environ.get("OPENAI_API_KEY")
print(f"OpenAI Key: {openai_key}")
client = OpenAI(api_key=openai_key)

def generate_content(data, prompt_config, internal_links):
    prompt = prompt_config

    # Replace placeholders with actual data
    for key in data:
        prompt = prompt.replace(f"{{{{{key}}}}}", data[key])

    prompt = prompt.replace("{{internal_links}}", ", ".join(internal_links))

    # Call OpenAI API using new SDK structure
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
