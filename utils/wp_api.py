import requests
from requests.auth import HTTPBasicAuth

username = 'Lorena'
app_password = 'q0wK 7z7E eKjW vhMw E1e8 KVPd'
site_url = 'https://planipets.com/blog'  # Not /blog

api_url = f"{site_url}/wp-json/wp/v2/pages"

def publish_to_wordpress(content, slug):
    page_data = {
        'title': slug,
        'content': content,
        'status': 'publish'
    }

    response = requests.post(api_url, json=page_data, auth=HTTPBasicAuth(username, app_password))

    print("Request URL:", api_url)
    print("Payload:", page_data)

    if response.status_code == 201:
        print("✅ Page published successfully!")
        print("Page URL:", response.json().get('link'))
        return response.json().get('link')
    else:
        print("❌ Failed to publish page.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)