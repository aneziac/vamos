from flask import Flask, request, jsonify, Response
from threading import Thread
from uuid import UUID, uuid1

from task import TaskStatus, TaskResponse
from transcribe import transcribe_audio
from database import get_task, init_db

app = Flask(__name__)


def get_transcript(task_id: UUID):
    pass


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileToUpload' not in request.files:
        return "No file part", 400

    file = request.files['fileToUpload']
    if file.filename == '':
        return "No selected file", 400

    file.save(f"./uploads/audio/{file.filename}")

    task_id = uuid1()
    thread = Thread(target=transcribe_audio, args=(file.filename, task_id))
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

    status_map: dict[TaskStatus, tuple[TaskResponse, int]] = {
        TaskStatus.PENDING: (TaskResponse("Task is still being processed."), 202),
        TaskStatus.FAILED: (TaskResponse("Task has failed."), 500),
        TaskStatus.COMPLETE: (TaskResponse("Task is complete.", get_transcript(task_uuid)), 200),
    }

    if task.status not in status_map:
        raise RuntimeError("Unrecognized task status")

    response, status_code = status_map[task.status]
    return jsonify(response.__dict__), status_code


if __name__ == '__main__':
    init_db()
    app.run(debug=True, threaded=True)
