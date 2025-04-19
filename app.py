from flask import Flask, request, render_template, redirect, url_for, jsonify
from waitress import serve
from werkzeug.utils import secure_filename
import csv, os, json
from utils import generate_content, publish_to_wordpress, create_slug, get_internal_links, md_to_html

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

pro = ''
city = ''
status_map = {}  # item_id -> "pending" | "success" | "fail" | "generating"

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
    global items
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_items = []
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    new_items.append(row)

            items = new_items
            for i in range(len(items)):
                status_map[i] = "pending"

            return redirect(url_for('upload_file'))

    # with open(prompt_config, 'r', encoding='utf-8') as f:
    #     prompt_config = json.load(f)
    return render_template('index.html', items=items, prompt_config=prompt_config, status_map=status_map)

@app.route('/generate-item/<int:item_id>', methods=['POST'])
def generate_item(item_id):
    status_map[item_id] = "generating"
    item = items[item_id]
    prompt_key = request.form.get("prompt_key", "template")
    slug = create_slug(item)
    pro = item['ville']
    city = item['metier']
    internal_links = get_internal_links(item)
    content = generate_content(item, prompt_config[prompt_key], internal_links)
    content = md_to_html(content, pro, city)

    try:
        resultUrl = publish_to_wordpress(content, slug)
        item["wordpress_url"] = resultUrl
        status_map[item_id] = "success"
        return jsonify({"status": "success", "url": resultUrl})
    except Exception as e:
        status_map[item_id] = "fail"
        return jsonify({"status": "fail", "error": str(e)})

@app.route('/cancel-generation/<int:item_id>', methods=['POST'])
def cancel_generation(item_id):
    status_map[item_id] = "fail"
    return jsonify({"status": "cancelled"})

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
    with open(config_path, "w", encoding='utf-8') as f:
        json.dump(prompt_config, f, ensure_ascii=False, indent=2)
    return jsonify({"success": True})

if __name__ == "__main__":
    # Check if we're in debug mode
    if app.debug:
        # If in debug mode, run with Flask's built-in server
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        # If not in debug mode, use Waitress
        serve(app, host="0.0.0.0", port=5000)