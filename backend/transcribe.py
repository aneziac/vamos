from uuid import UUID
import whisper
import logging

from task import Task, TaskStatus
from database import update_task


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

    srt_file = './uploads/transcripts/output.srt'
    with open(srt_file, "w") as f:
        for idx, segment in enumerate(segments):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            # SRT time format (HH:MM:SS,MS)
            start_time_srt = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time * 1000) % 1000):03}"
            end_time_srt = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02},{int((end_time * 1000) % 1000):03}"

            f.write(f"{idx + 1}\n")
            f.write(f"{start_time_srt} --> {end_time_srt}\n")
            f.write(f"{text}\n\n")

    logging.info(f"Transcription saved to: {srt_file}")

    update_task(Task(
        id=task_id,
        status=TaskStatus.COMPLETE
    ))
