# In a real app, fetch these from DB or a log of published slugs
existing_pages = {
    "austin": ["plumbing-residential-downtown-austin", "hvac-commercial-east-austin"]
}

def get_internal_links(row):
    city_key = row['ville'].lower()
    return existing_pages.get(city_key, [])