from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import csv, os, json
from utils import generate_content, publish_to_wordpress, create_slug, get_internal_links, md_to_html, delete_existing_page_by_slug

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

items = []
config_path = 'prompts/default.json'
prompt_config = json.load(open(config_path, encoding='utf-8'))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        for item in items:
            slug = create_slug(item)
            delete_existing_page_by_slug(slug)
        items.clear()
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    items.append(row)

    return render_template('index.html', items=items, prompt_config=prompt_config)

@app.route('/generate-item/<int:item_id>', methods=['POST'])
def generate_item(item_id):
    item = items[item_id]
    prompt_key = request.form.get("prompt_key", "default")
    if prompt_key == 'default':
        prompt_key = 'template'

    slug = create_slug(item)
    print("HHHHHHHHHHHHHHHHHHHHHHHH", slug)
    internal_links = get_internal_links(item)
    content = generate_content(item, prompt_config[prompt_key], internal_links)
    content = md_to_html(content)
    print('slugggggggggggggggg', slug)
    resultUrl = publish_to_wordpress(content, slug)
    item["wordpress_url"] = resultUrl

    return jsonify({"status": "success", "url": resultUrl})

@app.route('/item/<int:item_id>', methods=['POST'])
def open_item(item_id):
    item = items[item_id]
    resultUrl = item.get("wordpress_url")
    if not resultUrl:
        return jsonify({"error": "Not published yet"}), 400
    return jsonify({"url": resultUrl})

@app.route("/save-config", methods=["POST"])
def save_config():
    global prompt_config
    prompt_config = request.get_json()
    # Optionally, persist to file
    with open(config_path, "w") as f:
        json.dump(prompt_config, f)
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)
