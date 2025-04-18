import requests
from requests.auth import HTTPBasicAuth

username = 'Lorena'
app_password = 'q0wK 7z7E eKjW vhMw E1e8 KVPd'
site_url = 'https://planipets.com/blog'
api_url = f"{site_url}/wp-json/wp/v2/pages"

# ✅ Try to fetch by slug AND parent_id (with fallback to slug-only for debugging)
def get_page_by_slug_and_parent(slug, parent_id):
    slug = slug.strip().lower()
    response = requests.get(
        api_url,
        params={"slug": slug, "parent": parent_id},
        auth=HTTPBasicAuth(username, app_password)
    )
    if response.status_code == 200 and response.json():
        return response.json()[0]
    # 🐛 Fallback to just slug (debugging)
    response = requests.get(
        api_url,
        params={"slug": slug},
        auth=HTTPBasicAuth(username, app_password)
    )
    if response.status_code == 200 and response.json():
        print(f"⚠️ Page '{slug}' exists, but under a different parent ID: {response.json()[0]['parent']}")
        return response.json()[0]
    return None
# ✅ Publish to WordPress
def publish_to_wordpress(content, slug):
    parent_path = slug.strip('/').split('/')[:-1]  # All but last
    page_slug = slug.strip('/').split('/')[-1]     # Final leaf slug
    parent_id = 0  # Start at root
    created_parent_ids = {}  # Optional cache

    # 🧱 Step 1: Re-use or create parent pages
    for part in parent_path:
        existing_page = get_page_by_slug_and_parent(part, parent_id)
        if existing_page:
            parent_id = existing_page['id']
            print(f"✅ Found existing parent: {part} (ID: {parent_id})")
        else:
            print(f"➕ Creating parent: {part}")
            parent_data = {
                "title": part.replace('-', ' ').title(),
                "slug": part,
                "status": "publish",
                "parent": parent_id
            }
            res = requests.post(api_url, json=parent_data, auth=HTTPBasicAuth(username, app_password))
            if res.status_code == 201:
                parent_id = res.json().get('id', 0)
            else:
                print(f"❌ Failed to create parent '{part}': {res.text}")
                return '/'

    # 🗑️ Step 2: Delete leaf page if it exists under final parent
    existing_leaf = get_page_by_slug_and_parent(page_slug, parent_id)
    if existing_leaf:
        delete_url = f"{api_url}/{existing_leaf['id']}?force=true"
        del_res = requests.delete(delete_url, auth=HTTPBasicAuth(username, app_password))
        if del_res.status_code == 200:
            print(f"🗑️ Deleted existing leaf page: {page_slug}")
        else:
            print(f"⚠️ Failed to delete existing page: {del_res.text}")

    # 📝 Step 3: Create new leaf page
    page_data = {
        "title": page_slug.replace('-', ' ').title(),
        "slug": page_slug,
        "content": f"<style>.entry-title{{display:none !important}}</style>{content}",
        "status": "publish",
        "parent": parent_id
    }

    response = requests.post(api_url, json=page_data, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 201:
        link = response.json().get('link')
        print("✅ Page published successfully!")
        print("🔗 Page URL:", link)
        return link
    else:
        print("❌ Failed to publish page.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return '/'
