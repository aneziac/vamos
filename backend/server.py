from flask import Flask, request
import whisper  # type: ignore
from threading import Thread


model = whisper.load_model('base')
app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileToUpload' not in request.files:
        return "No file part", 400

    file = request.files['fileToUpload']
    if file.filename == '':
        return "No selected file", 400

    # Save the file to a directory
    file.save(f"./uploads/{file.filename}")
    return "File uploaded successfully", 200


@app.route('/transcribe', methods=['POST'])
def post_transcript():
    # create transcript
    transcript = model.transcribe(f"./uploads/{file.filename}")

    print(transcript['text'])


if __name__ == '__main__':
    app.run(debug=True)
