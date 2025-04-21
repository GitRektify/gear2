import requests
from requests.auth import HTTPBasicAuth

# WordPress credentials
username = 'Lorena'
app_password = 'q0wK 7z7E eKjW vhMw E1e8 KVPd'
site_url = 'https://planipets.com/blog'
api_url = f"{site_url}/wp-json/wp/v2/pages"

# Get a page by slug and parent ID
def get_page_by_slug_and_parent(slug, parent_id):
    slug = slug.strip().lower()
    # First try with parent ID
    response = requests.get(api_url, params={"slug": slug, "parent": parent_id}, auth=HTTPBasicAuth(username, app_password))
    if response.status_code == 200 and response.json():
        return response.json()[0]
    
    # Fallback to slug-only (debug)
    response = requests.get(api_url, params={"slug": slug}, auth=HTTPBasicAuth(username, app_password))
    if response.status_code == 200 and response.json():
        print(f"⚠️ Found page '{slug}' but with different parent ID: {response.json()[0]['parent']}")
        return response.json()[0]
    
    return None

# Publish content to WordPress as a Page
def publish_to_wordpress(content, slug, extra_data=None):
    slug_parts = slug.strip('/').split('/')
    page_slug = slug_parts[-1]
    parent_path = slug_parts[:-1]
    parent_id = 0

    print(f"\n🚀 Publishing page: /{'/'.join(slug_parts)}")

    # Create or reuse parent hierarchy
    for part in parent_path:
        existing_page = get_page_by_slug_and_parent(part, parent_id)
        if existing_page:
            parent_id = existing_page['id']
            print(f"✅ Found parent: {part} (ID: {parent_id})")
        else:
            print(f"➕ Creating parent page: {part}")
            new_page_data = {
                "title": part.replace('-', ' ').title(),
                "slug": part,
                "status": "publish",
                "parent": parent_id
            }
            res = requests.post(api_url, json=new_page_data, auth=HTTPBasicAuth(username, app_password))
            if res.status_code == 201:
                parent_id = res.json().get('id')
            else:
                print(f"❌ Error creating parent '{part}':", res.text)
                return None

    # Delete existing leaf page if it exists
    existing_leaf = get_page_by_slug_and_parent(page_slug, parent_id)
    if existing_leaf:
        delete_url = f"{api_url}/{existing_leaf['id']}?force=true"
        del_res = requests.delete(delete_url, auth=HTTPBasicAuth(username, app_password))
        if del_res.status_code == 200:
            print(f"🗑️ Deleted existing page: {page_slug}")
        else:
            print(f"⚠️ Could not delete existing page: {del_res.text}")

    # Inject WebPage schema
    schema = f"""
    <script type="application/ld+json">
    {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "{page_slug.replace('-', ' ').title()}",
    "url": "{site_url}/{slug.strip('/')}"
    }}
    </script>
    """

    # Final page content and data
    page_data = {
        "title": page_slug.replace('-', ' ').title(),
        "slug": page_slug,
        "content": f"{schema}<style>.entry-title{{display:none !important}}</style>{content}",
        "status": "publish",
        "parent": parent_id
    }

    # Optionally add more fields like template, author, etc.
    if extra_data:
        page_data.update(extra_data)

    # Create the new page
    response = requests.post(api_url, json=page_data, auth=HTTPBasicAuth(username, app_password))
    if response.status_code == 201:
        page_url = response.json().get('link')
        print(f"✅ Page published: {page_url}")
        return page_url
    else:
        print(f"❌ Failed to publish page '{page_slug}': {response.status_code}")
        print("Response:", response.text)
        return None
