import pandas as pd
import json

# === Step 1: Load CSV file ===
csv_filename = "E:/Upwork/real_top1000_villes_latlng.csv"  # Change this to your file path if needed

try:
    df = pd.read_csv(csv_filename)
    print(f"✅ Loaded CSV file: {csv_filename}")
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit(1)

# === Step 2: Convert to JSON format (list of dictionaries) ===
json_data = df.to_dict(orient="records")

# === Step 3: Save to a .json file ===
json_filename = "cities.json"
try:
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    print(f"✅ JSON saved to: {json_filename}")
except Exception as e:
    print(f"❌ Error saving JSON: {e}")
    exit(1)

# === Step 4: Print the result ===
print("🔍 JSON Preview:")
print(json.dumps(json_data[:3], indent=4, ensure_ascii=False))  # Preview first 3 rows
