import os
import uuid
import logging
from datetime import datetime, timedelta
# from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== CONFIGURATION ==========
# Load variables from .env file
# load_dotenv()

# API_KEY = os.getenv("GENAI_API_KEY", None)
# if not API_KEY:
#     raise RuntimeError("GENAI_API_KEY not set in environment")
# genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel("gemini‑2.5-flash")


API_KEY = "AIzaSyALLofGfhSp_OvH8cFcdN0II66Qu6R5MnM"  # Replace with your API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)
CORS(app)

RAW_UPLOAD_FOLDER = "uploads_raw"
PROCESSED_FOLDER = "uploads_processed"
os.makedirs(RAW_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# ========== IMAGE PROCESSING FUNCTION ==========
def process_image(input_path, output_path, max_size=(1200,800), quality=80, remove_bg=False):
    try:
        img = Image.open(input_path)
        img = img.convert("RGB")  # ensure RGB

        if remove_bg:
            logger.info(f"Background removal requested but not implemented")

        # Resize preserving aspect ratio
        img.thumbnail(max_size, Image.LANCZOS)

        # Save compressed version
        img.save(output_path, format="JPEG", quality=quality, optimize=True)

        return output_path
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise

# ========== IMAGE CLASSIFICATION FUNCTION ==========
def is_property_image(image_path):
    """Return True if the image looks like a property, else False."""
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        prompt = (
            "Classify this image. "
            "Return 'property' if it is a real estate property (house, apartment, building), "
            "otherwise return 'other'."
        )

        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        )

        if response and response.candidates:
            classification = response.candidates[0].content.parts[0].text.strip().lower()
            return classification == "property"
        return False
    except Exception as e:
        logger.error(f"Error classifying image: {e}")
        return False

# ========== CAPTION GENERATION FUNCTION ==========
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
            [prompt, {"mime_type":"image/jpeg", "data": image_bytes}]
        )

        if response and response.candidates:
            caption = response.candidates[0].content.parts[0].text.strip()
            return caption
        else:
            return "⚠️ No caption generated."
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        return "❌ Error generating caption."

# ========== ROUTE ==========
@app.route("/generate_caption", methods=["POST"])
def generate_caption_route():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    unique_id = uuid.uuid4().hex
    original_filename = file.filename
    raw_path = os.path.join(RAW_UPLOAD_FOLDER, f"{unique_id}_{original_filename}")
    file.save(raw_path)

    try:
        # Process the image
        processed_filename = f"{unique_id}_proc_{original_filename}"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        process_image(raw_path, processed_path, max_size=(1200,800), quality=80, remove_bg=False)

        # Check if the image is a property
        if is_property_image(processed_path):
            caption = generate_property_caption(processed_path)
        else:
            caption = "❌ No property description available for this image."

        # Simulate social media post preparation
        platforms = ["instagram", "facebook"]
        schedule_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"

        post_object = {
            "image_filename": processed_filename,
            "caption": caption,
            "platforms": platforms,
            "scheduled_time": schedule_time
        }

        return jsonify({"post": post_object}), 200

    except Exception as e:
        logger.error(f"Route failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
