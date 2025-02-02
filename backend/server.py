from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from threading import Thread
from uuid import UUID, uuid1

from task import TaskPayload, TaskStatus
from transcribe import transcribe_audio
from database import get_task, init_db

app = Flask(__name__)
CORS(app)


def get_transcript(task_id: UUID):
    return open(f"./uploads/transcripts/{task_id}.srt").read()


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
    thread = Thread(target=transcribe_audio, args=(upload_path, task_id))
    thread.start()

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
        return jsonify({"status": "error", "message": "Invalid task ID"}), 400

    task = get_task(task_uuid)

    if not task:
        return jsonify({"status": "not found", "message": "Task not found"}), 404

    status_map: dict[TaskStatus, tuple[TaskPayload, int]] = {
        TaskStatus.PENDING: (TaskPayload("Task is still being processed.", TaskStatus.PENDING), 202),
        TaskStatus.FAILED: (TaskPayload("Task has failed.", TaskStatus.FAILED), 500),
        TaskStatus.COMPLETE: (TaskPayload("Task is complete.", TaskStatus.COMPLETE, get_transcript(task_uuid)), 200),
    }

    if task.status not in status_map:
        raise RuntimeError("Unrecognized task status")

    response, status_code = status_map[task.status]
    return jsonify(response.__dict__), status_code


if __name__ == '__main__':
    init_db()
    app.run(debug=True, threaded=True)
