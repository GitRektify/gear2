def create_slug(row):
    parts = [row['metier'], row['animal'], row['ville']]
    if row.get('quartier'):
        parts.append(row['quartier'])
    if row.get('specificite'):
        parts.append(row['specificite'])
    slug = '/'.join(p.lower().replace(' ', '-') for p in parts if p)
    return slug  # no '/blog' here
