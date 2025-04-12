from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import csv, os, json
from utils import generate_content, publish_to_wordpress, create_slug, get_internal_links

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

items = []
prompt_config = json.load(open('prompts/default.json'))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Is choosed file csv file?
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    items.clear()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)   # Ensures that uploaded filenames are safe to use (removes dangerous characters, etc.).
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            items.clear()
            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # if not row['quartier'] or row['ville'].lower() in ['smalltown1', 'smalltown2']:
                    #     continue
                    items.append(row)
    return render_template('index.html', items=items, prompt_config = prompt_config)


@app.route('/item/<int:item_id>')
def open_item(item_id):
    # Load the CSV file again, or better — store the parsed items globally if already loaded
    item = items[item_id]
    slug = create_slug(item)
    internal_links = get_internal_links(item)
    content = generate_content(item, prompt_config, internal_links)
    resultUrl = publish_to_wordpress(content, slug)
    # return redirect(resultUrl)
    return redirect(resultUrl)


if __name__ == '__main__':
    app.run(debug=True)
