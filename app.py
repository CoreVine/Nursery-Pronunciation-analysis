from flask import Flask, request, jsonify, send_file
import numpy as np
import whisper
from gtts import gTTS
import os
import noisereduce as nr
import Levenshtein
import uuid
from werkzeug.utils import secure_filename
import soundfile as sf
import logging
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
fs = 44100  # Sample rate
current_language = 'en'
models = {"en": whisper.load_model("small.en"), "ar": whisper.load_model("small")}

# Helper functions
def clean_text(text, language):
    if language == "ar":
        replacements = {
            "أ": "ا", "إ": "ا", "آ": "ا",
            "ة": "ه", "ى": "ي", "ئ": "ء", "ؤ": "ء"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
    return text.strip()

def calculate_accuracy(target, actual):
    if not target or not actual:
        return 0
    distance = Levenshtein.distance(target, actual)
    max_len = max(len(target), len(actual))
    return max(0, 100 - (distance / max_len * 100))

def generate_feedback(target, actual, accuracy, language):
    if not target or not actual:
        return "Could not understand. Please try again." if language == "en" else "لم أتمكن من الفهم. حاول مرة أخرى"
    if accuracy > 95:
        return "🌟 Excellent pronunciation! Perfectly said!" if language == "en" else "🌟 ممتاز! النطق واضح وصحيح تمامًا"
    elif accuracy > 90:
        base_feedback = "Good, but needs slight improvement:" if language == "en" else "جيد، ولكن يحتاج تحسينًا بسيطًا:"
    else:
        base_feedback = "Needs improvement:" if language == "en" else "يحتاج تحسينًا:"
    return base_feedback

def cleanup_old_files():
    """Delete files older than 24 hours from the upload folder."""
    now = datetime.now()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_mtime > timedelta(hours=24):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {str(e)}")

@app.route('/')
def home():
    """API information"""
    return jsonify({
        "status": "success", 
        "message": "Pronunciation Coach API is running",
        "endpoints": {
            "/upload_audio": "POST - Upload and analyze audio",
            "/get_audio/<filename>": "GET - Retrieve audio file",
            "/set_language": "POST - Set language for analysis"
        }
    })

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set the current language."""
    global current_language
    data = request.json
    lang = data.get('language', 'en')
    if lang not in models:
        return jsonify({'status': 'error', 'message': 'Invalid language'}), 400
    current_language = lang
    return jsonify({'status': 'success', 'language': lang})

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """Upload and analyze audio."""
    try:
        target_text = request.form.get('text', '').strip()
        language = request.form.get('language', 'en')

        if not target_text:
            return jsonify({'status': 'error', 'message': 'No text provided'}), 400
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        filename = secure_filename(f"uploaded_{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        logger.info(f"Audio file uploaded and saved to {file_path}")

        data, samplerate = sf.read(file_path)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        cleaned_audio = nr.reduce_noise(
            y=data,
            sr=samplerate,
            prop_decrease=0.8 if language == 'ar' else 0.9,
            n_fft=1024
        )

        cleaned_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"cleaned_{uuid.uuid4()}.wav")
        sf.write(cleaned_filename, cleaned_audio, samplerate)

        logger.info(f"Cleaned audio saved to {cleaned_filename}")

        model = models[language]
        result = model.transcribe(
            cleaned_filename,
            language=language,
            initial_prompt=target_text,
            temperature=0.2
        )
        user_text = clean_text(result["text"].strip(), language)

        accuracy = calculate_accuracy(target_text, user_text)
        feedback = generate_feedback(target_text, user_text, accuracy, language)

        tts_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"tts_{uuid.uuid4()}.mp3")
        tts = gTTS(text=target_text, lang=language, slow=True)
        tts.save(tts_filename)

        response = {
            'status': 'success',
            'target_text': target_text,
            'user_text': user_text,
            'accuracy': accuracy,
            'feedback': feedback,
            'recording_url': f"/get_audio/{os.path.basename(file_path)}",
            'correct_pronunciation_url': f"/get_audio/{os.path.basename(tts_filename)}"
        }
        return jsonify(response)
    except Exception as e:
        logger.error(f"Upload audio error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Serve audio files."""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        return send_file(filepath, mimetype='audio/mp3')
    except Exception as e:
        logger.error(f"Audio file error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    cleanup_old_files()
    app.run(host='0.0.0.0', port=5000, debug=True)