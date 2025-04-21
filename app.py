
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from waitress import serve
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import csv, os, json
from utils import generate_content, publish_to_wordpress, create_slug, get_internal_links, md_to_html

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key'  # Replace with a secure, random key in production

config_path = 'prompts/default.json'
prompt_config = json.load(open(config_path, encoding='utf-8'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global base_url
    base_url = request.url_root
    print(base_url)

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

            session['items'] = new_items
            session['status_map'] = {str(i): "pending" for i in range(len(new_items))}

            return redirect(url_for('upload_file'))

    return render_template(
        'index.html',
        items=session.get('items', []),
        prompt_config=prompt_config,
        status_map=session.get('status_map', {})
    )

@app.route('/generate-item/<int:item_id>', methods=['POST'])
def generate_item(item_id):
    items = session.get('items', [])
    status_map = session.get('status_map', {})

    if item_id >= len(items):
        return jsonify({"status": "fail", "error": "Invalid item ID"}), 400

    status_map[str(item_id)] = "generating"
    session['status_map'] = status_map

    item = items[item_id]
    prompt_key = request.form.get("prompt_key", "template")
    slug = create_slug(item)
    pro = item['ville']
    city = item['metier']
    internal_links = get_internal_links(item)

    content, objects =  generate_content(item, prompt_config[prompt_key], internal_links)
    print("oooooooooooo", objects)
    content = md_to_html(content, pro, city, objects, base_url)

    try:
        resultUrl = publish_to_wordpress(content, slug)
        item["wordpress_url"] = resultUrl
        items[item_id] = item
        session['items'] = items
        status_map[str(item_id)] = "success"
        session['status_map'] = status_map
        return jsonify({"status": "success", "url": resultUrl})
    except Exception as e:
        status_map[str(item_id)] = "fail"
        session['status_map'] = status_map
        return jsonify({"status": "fail", "error": str(e)})

@app.route('/cancel-generation/<int:item_id>', methods=['POST'])
def cancel_generation(item_id):
    status_map = session.get('status_map', {})
    status_map[str(item_id)] = "fail"
    session['status_map'] = status_map
    return jsonify({"status": "cancelled"})

@app.route('/item/<int:item_id>', methods=['POST'])
def open_item(item_id):
    items = session.get('items', [])
    if item_id >= len(items):
        return jsonify({"error": "Invalid item ID"}), 400

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

@app.route('/generate-item', methods=['POST'])
def generate_item_from_object():
    data = request.get_json()
    item = data.get("item")
    if not item:
        return jsonify({"status": "fail", "error": "No item provided"}), 400

    prompt_key = item.get("prompt_key", "template")
    slug = create_slug(item)
    pro = item['ville']
    city = item['metier']
    internal_links = get_internal_links(item)

    try:
        content, objects = generate_content(item, prompt_config[prompt_key], internal_links)
        content = md_to_html(content, pro, city, objects, base_url)
        resultUrl = publish_to_wordpress(content, slug)
        return jsonify({"status": "success", "url": resultUrl})
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)})

# if __name__ == "__main__":
#     # If in debug mode, run with Flask's built-in server
#     port = int(os.environ.get("PORT", 5000))
#     serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Check if we're in debug mode
    if app.debug:
        print("debug mode")
        # If in debug mode, run with Flask's built-in server
        port = int(os.environ.get("PORT", 5000))
        app.run(debug=True, host="0.0.0.0", port=port)
    else:
        print("serve mode")
        # If not in debug mode, use Waitressv
        port = int(os.environ.get("PORT", 5000))
        serve(app, host="0.0.0.0", port=port)
