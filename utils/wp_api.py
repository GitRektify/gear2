import requests
from requests.auth import HTTPBasicAuth

username = 'Lorena'
app_password = 'q0wK 7z7E eKjW vhMw E1e8 KVPd'
site_url = 'https://planipets.com/blog'  # Not /blog

api_url = f"{site_url}/wp-json/wp/v2/pages"

def get_existing_content_by_slug(slug):
    post_types = ['pages', 'posts']
    for post_type in post_types:
        response = requests.get(
            f"{site_url}/wp-json/wp/v2/{post_type}?slug={slug}",
            auth=HTTPBasicAuth(username, app_password)
        )
        if response.status_code == 200 and response.json():
            return response.json()[0], post_type  # Return first match and type
    return None, None

def delete_existing_page_by_slug(slug):
    page, post_type = get_existing_content_by_slug(slug)
    if page:
        delete_url = f"{site_url}/wp-json/wp/v2/{post_type}/{page['id']}?force=true"
        response = requests.delete(delete_url, auth=HTTPBasicAuth(username, app_password))
        if response.status_code == 200:
            print(f"🗑️ Deleted existing {post_type[:-1]} with slug '{slug}' (ID: {page['id']})")
        else:
            print(f"❌ Failed to delete {post_type}: {response.status_code}, {response.text}")

def get_or_create_page(title, slug, parent=None):
    # Check if the page exists
    params = {'slug': slug}
    if parent:
        params['parent'] = parent

    response = requests.get(api_url, params=params, auth=HTTPBasicAuth(username, app_password))
    pages = response.json()

    if pages and isinstance(pages, list):
        return pages[0]['id']

    # Page doesn't exist, create it
    data = {
        'title': title,
        'slug': slug,
        'status': 'publish',
    }
    if parent:
        data['parent'] = parent

    response = requests.post(api_url, json=data, auth=HTTPBasicAuth(username, app_password))
    if response.status_code == 201:
        return response.json()['id']
    else:
        print(f"Error creating page '{title}':", response.text)
        return None

def publish_to_wordpress(content, slug):
    # 🔥 Delete existing page first (if any)
    delete_existing_page_by_slug(slug)
    page_data = {
        'title': '',
        'slug' : slug.split('/')[-1],
        'content': content,
        'status': 'publish'
    }

    # Set full path
    parent_path = slug.strip('/').split('/')[:-1]
    parent_slug = ''
    parent_id = 0

# Create parent pages if necessary
    for part in parent_path:
        response = requests.get(
            f"{site_url}/wp-json/wp/v2/pages",
            params={"slug": part},
            auth=HTTPBasicAuth(username, app_password)
        )
        if response.status_code == 200 and response.json():
            parent_id = response.json()[0]['id']
        else:
            # Create parent if not exist
            parent_page = {
                "title": part.replace('-', ' ').title(),
                "slug": part,
                "status": "publish",
                "parent": parent_id
            }
            create_res = requests.post(api_url, json=parent_page, auth=HTTPBasicAuth(username, app_password))
            parent_id = create_res.json().get('id', 0)

    # Now create the actual page
    page_data['parent'] = parent_id

    response = requests.post(api_url, json=page_data, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 201:
        print("✅ Page published successfully!")
        print("Page URL:", response.json().get('link'))
        return response.json().get('link')
    else:
        print("❌ Failed to publish page.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return '/'