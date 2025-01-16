
import os
from flask import Flask, render_template, request, redirect, url_for, send_file
import speech_recognition as sr
from gtts import gTTS

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def text_to_speech(text):
    """Convert text to speech using gTTS and save as MP3."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp3')
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        print(f"Error converting text to speech: {e}")
        return None

@app.route('/')
def upload_page():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Perform speech recognition on the uploaded file
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(file_path) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)

                # Convert the transcribed text to speech
                audio_path = text_to_speech(text)
                if audio_path is None:
                    return "Failed to convert text to speech."

                # Return the MP3 file for download
                return send_file(audio_path, as_attachment=True, download_name='output.mp3')

        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"Error with the Google Speech Recognition service: {e}"

    return redirect(url_for('upload_page'))


if __name__ == '__main__':
    app.run(debug=True)
