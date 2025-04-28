# Pronunciation Coach API

This repository provides an API for analyzing pronunciation in both English and Arabic. It uses Whisper for transcription and gTTS for text-to-speech. The API allows users to upload audio files, transcribe them, analyze pronunciation accuracy, and provide feedback.

---

## Features

- **Language Support**: English (`en`) and Arabic (`ar`).
- **Audio Analysis**: Noise reduction and transcription using Whisper.
- **Pronunciation Feedback**: Calculates accuracy and generates feedback.
- **Text-to-Speech**: Generates correct pronunciations using gTTS.
- **File Cleanup**: Automatically deletes temporary files older than 24 hours.
- **Dockerized**: Ready for deployment with Docker and Docker Compose.

---

## Requirements

- Python 3.9+
- Docker (for containerized execution)
- ffmpeg (required for Whisper)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/AhmedHanySaber/pronunciation-coach-api.git
cd pronunciation-coach-api
```

### 2. Install Dependencies
Using Python:
```bash
pip install -r requirements.txt
```

---

## Running the API

### Option 1: Locally with Python
1. **Start the API**:
   ```bash
   python app.py
   ```
2. **Access the API**:
   - The API will be available at: `http://127.0.0.1:5000`

---

### Option 2: Using Docker
1. **Build the Docker Image**:
   ```bash
   docker build -t pronunciation-coach .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 5000:5000 pronunciation-coach
   ```

3. **Access the API**:
   - The API will be available at: `http://127.0.0.1:5000`

---

### Option 3: Using Docker Compose
1. **Start the Services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the API**:
   - The API will be available at: `http://127.0.0.1:5000`

---

## API Endpoints

### **GET /** - Home
Renders the interactive web interface.

### **POST /set_language**
Sets the current language for transcription and feedback.
- **Body Parameters**:
  - `language`: `"en"` (English) or `"ar"` (Arabic)

### **POST /upload_audio**
Uploads and processes an audio file.
- **Form Data**:
  - `text`: The target text to practice.
  - `language`: `"en"` or `"ar"`.
  - `file`: The audio file to upload.
- **Response**:
  - `status`: `"success"` or `"error"`.
  - `target_text`: The input text.
  - `user_text`: The transcribed text.
  - `accuracy`: Pronunciation accuracy (percentage).
  - `feedback`: Detailed feedback.
  - `recording_url`: URL to the processed audio.
  - `correct_pronunciation_url`: URL to the correct pronunciation audio.

### **GET /get_audio/<filename>**
Serves audio files (processed or generated).
- **Path Parameter**:
  - `filename`: The requested audio file.

---

## Deployment

### On a VPS Server
1. **Pull the Repository**:
   ```bash
   git clone https://github.com/AhmedHanySaber/pronunciation-coach-api.git
   cd pronunciation-coach-api
   ```

2. **Build and Run with Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

3. **Setup Reverse Proxy (Optional)**:
   - Use Nginx or Apache to forward traffic to `http://127.0.0.1:5000`.

---

## Scheduled Cleanup for Temporary Files
The app automatically deletes temporary files older than 24 hours on startup. To ensure consistent cleanup, you can set up a cron job or a task scheduler to restart the application daily.

Example cron job:
```bash
0 0 * * * docker-compose restart
```

---

## Notes
- Ensure your VPS has sufficient resources, as Whisper can be resource-intensive.
- If deploying on a server, consider using HTTPS for secure communication.

---

## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.