import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import google.generativeai as genai

# ========== CONFIGURATION ==========
API_KEY = "AIzaSyALLofGfhSp_OvH8cFcdN0II66Qu6R5MnM"  # Replace with your API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ========== IMAGE TO CAPTION FUNCTION ==========
def generate_property_caption(image_path):
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        prompt = (
            "You are a real estate marketing expert. "
            "Describe this property image in a short, professional caption suitable for Instagram. "
            "Mention type, vibe, and visible features."
        )

        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        )

        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()

        return "⚠️ No caption generated."

    except Exception as e:
        print(f"❌ Error: {e}")
        return "❌ Error generating caption."


# ========== ROUTE ==========
@app.route("/generate_caption", methods=["POST"])
def generate_caption():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    caption = generate_property_caption(path)
    return jsonify({"caption": caption})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
