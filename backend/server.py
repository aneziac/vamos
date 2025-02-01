from flask import Flask, request
import whisper  # type: ignore
from threading import Thread
import transcribe
from pydub import AudioSegment


model = whisper.load_model('base')
app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileToUpload' not in request.files:
        return "No file part", 400

    file = request.files['fileToUpload']
    if file.filename == '':
        return "No selected file", 400

    file.save(f"./uploads/audio/{file.filename}")

    audio = AudioSegment.from_file(file.stream, format='mp3')
    transcribe.transcribe_with_whisper(audio, f"./uploads/transcripts/{file.filename}")

    # Save the file to a directory
    return "File uploaded successfully", 200


@app.route('/transcribe', methods=['POST'])
def post_transcript():
    # create transcript
    transcript = model.transcribe(f"./uploads/{file.filename}")

    print(transcript['text'])


if __name__ == '__main__':
    app.run(debug=True)
