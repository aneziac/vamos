from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from threading import Thread
from uuid import UUID, uuid1
import logging

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
    youtube_link = request.form.get('youtubeLink')
    return youtube_link, 200


@app.route('/upload', methods=['POST'])
def upload_file() -> tuple[Response | str, int]:
    if 'fileToUpload' not in request.files:
        return "No file part", 400

    file = request.files['fileToUpload']
    if file.filename == '':
        return "No selected file", 400

    upload_path = f"./uploads/audio/{file.filename}"
    file.save(upload_path)

    task_id = uuid1()
    thread = Thread(target=transcribe_handler, args=(upload_path, task_id, app.logger))
    thread.start()

    app.logger.info(f'Created transcription task with ID {task_id}')

    return jsonify({
        "status": TaskStatus.PENDING,
        "message": "Your request is being processed.",
        "task_id": str(task_id)
    }), 202


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