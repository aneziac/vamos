# type: ignore
from uuid import UUID
import whisper
import logging

from task import Task, TaskStatus
from database import update_task


# SRT time format (HH:MM:SS,MS)
def srt_time_format(t):
    return f"{int(t // 3600):02}:" \
           f"{int((t % 3600) // 60):02}:" \
           f"{int(t % 60):02}," \
           f"{int((t * 1000) % 1000):03}"


def transcribe_audio(audio_path: str, task_id: UUID):
    # could be base/small/medium
    model = whisper.load_model("base")

    # Temporarily assume language is english
    result = model.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
    )

    segments = result["segments"]

    srt_file = f'./uploads/transcripts/{task_id}.srt'
    with open(srt_file, "w") as f:
        for idx, segment in enumerate(segments):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            f.write(f"{idx + 1}\n")
            f.write(f"{srt_time_format(start_time)} --> {srt_time_format(end_time)}\n")
            f.write(f"{text}\n\n")

    logging.info(f"Transcription saved to: {srt_file}")

    update_task(Task(
        id=task_id,
        status=TaskStatus.COMPLETE
    ))
