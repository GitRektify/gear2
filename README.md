# Local Service Page Publisher

Uploads a CSV with location/service combos → Generates content with GPT → Publishes via WordPress API.

## How to Run
1. Install dependencies: `pip install flask openai python-dotenv requests`
2. Create `.env` file (see example)
3. Run the app: `python app.py`
4. Visit `http://localhost:5000`

## Prompts
Edit the JSON in `prompts/default.json` to control the page structure.