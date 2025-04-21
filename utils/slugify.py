import unicodedata

def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def create_slug(row):
    parts = [row['metier'], row['animal'], row['ville']]
    if row.get('quartier'):
        parts.append(row['quartier'])
    if row.get('specificite'):
        parts.append(row['specificite'])
    slug = '/'.join(p.lower().replace(' ', '-') for p in parts if p)
    return remove_accents(slug)  # no '/blog' here
