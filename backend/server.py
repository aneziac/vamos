from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from flask_cors import CORS
from threading import Thread
from uuid import UUID, uuid1
import logging
from typing import Callable
import yt_dlp
import os

from task import TaskPayload, TaskStatus
from transcribe import transcribe_handler
from database import get_task, init_db

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
CORS(app)


def get_transcript(task_id: UUID):
    return open(f"./uploads/transcripts/{task_id}.srt").read()


@app.after_request
def log_errors(response):
    log_message = f"{response.status_code} - {response.get_data(as_text=True).strip()}"

    if response.status_code >= 400:
        app.logger.error(log_message)

    return response


@app.route('/video', methods=['POST'])
def handle_video() -> tuple[Response | str, int]:
    link = request.form.get('youtubeLink')

    base_path = './uploads/audio/'
    # https://stackoverflow.com/questions/75867758/how-to-extract-only-audio-from-downloading-video-python-yt-dlp
    with yt_dlp.YoutubeDL({
        'extract_audio': True,
        'format': 'bestaudio',
        'outtmpl': base_path + '%(title)s.mp3'
    }) as video:
        info_dict = video.extract_info(link, download=True)
        video_title = info_dict['title']
        video.download(link)

    task_id = new_task(transcribe_handler, (base_path + video_title + '.mp3',))

    return jsonify({
        "status": TaskStatus.PENDING,
        "message": "Your request is being processed.",
        "task_id": str(task_id)
    }), 202


@app.route('/upload', methods=['POST'])
def upload_file() -> tuple[Response | str, int]:
    if 'fileToUpload' not in request.files:
        return "No file part", 400

    file = request.files['fileToUpload']
    if file.filename == '':
        return "No selected file", 400

    upload_path = f"./uploads/audio/{file.filename}"
    file.save(upload_path)

    task_id = new_task(transcribe_handler, (upload_path,))

    return jsonify({
        "status": TaskStatus.PENDING,
        "message": "Your request is being processed.",
        "task_id": str(task_id)
    }), 202

@app.route('/download/<task_id>')
def download_transcript(task_id: str):
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return jsonify({"error": f"Invalid task ID: {task_id}"}), 400

    task = get_task(task_uuid)
    if not task:
        return jsonify({"error": f"Task {task_id} not found"}), 404

    if task.status != TaskStatus.COMPLETE:
        return jsonify({"error": f"Task {task_id} is not yet complete"}), 400

    transcript_dir = os.path.join(os.getcwd(), 'uploads', 'transcripts')
    transcript_path = os.path.join(transcript_dir, f"{task_uuid}.srt")

    app.logger.debug(f"Serving transcript from {transcript_path}")

    if not os.path.exists(transcript_path):
        app.logger.error(f"Transcript for task {task_id} not found at {transcript_path}")
        return jsonify({"error": f"Transcript for task {task_id} not found"}), 404

    try:
        return send_from_directory(transcript_dir, f"{task_uuid}.srt", as_attachment=True)
    except Exception as e:
        app.logger.exception(f"Error sending file for task {task_id}: {str(e)}")
        return jsonify({"error": "Internal server error while sending file"}), 500

def new_task(f: Callable, args: tuple) -> UUID:
    task_id = uuid1()
    thread = Thread(target=f, args=(*args, task_id, app.logger))
    thread.start()

    app.logger.info(f'Created transcription task with ID {task_id}')
    return task_id


@app.route('/status/<task_id>', methods=['GET'])
def get_task_route(task_id: str) -> tuple[Response, int]:
    """Retrieve task status and return a JSON response."""
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        return f"Invalid task ID: {task_id}", 400

    task = get_task(task_uuid)

    if not task:
        return f"Task {task_id} not found", 404

    status_map: dict[TaskStatus, tuple[TaskPayload, int]] = {
        TaskStatus.PENDING: (TaskPayload("Task is still being processed.", TaskStatus.PENDING), 202),
        TaskStatus.FAILED: (TaskPayload("Task has failed.", TaskStatus.FAILED), 500),
        TaskStatus.COMPLETE: (TaskPayload("Task is complete.", TaskStatus.COMPLETE), 200),
    }

    if task.status not in status_map:
        return f"Unrecognized task status: {task.status}", 500

    response, status_code = status_map[task.status]
    if response.status == TaskStatus.COMPLETE:
        response.transcript = get_transcript(task_uuid)

    return jsonify(response.__dict__), status_code


if __name__ == '__main__':
    init_db()
    app.run(debug=True, threaded=True)