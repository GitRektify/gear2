def create_slug(row):
    parts = [row['ville'], row['quartier'], row['metier'], row['animal'], row['specificite']]
    return '-'.join(p.lower().replace(' ', '-') for p in parts if p)