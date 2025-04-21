# type: ignore
from uuid import UUID
import whisper
from logging import Logger
import warnings

from task import Task, TaskStatus
from database import update_task


# suppress torch.load warning
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")


# SRT time format (HH:MM:SS,MS)
def srt_time_format(t):
    return f"{int(t // 3600):02}:" \
           f"{int((t % 3600) // 60):02}:" \
           f"{int(t % 60):02}," \
           f"{int((t * 1000) % 1000):03}"


def transcribe_audio(audio_path: str, task_id: UUID, logger: Logger):
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

            #f.write(f"{idx + 1}\n")
            #f.write(f"{srt_time_format(start_time)} --> {srt_time_format(end_time)}\n")
            if(text != ""):
                f.write(f"{text}\n")
            else:
                f.write(f"...\n")

    logger.info(f"Transcript saved to: {srt_file}")


def transcribe_handler(audio_path: str, task_id: UUID, logger: Logger):
    update_task(Task(
        id=task_id,
        status=TaskStatus.PENDING
    ))

    status = TaskStatus.COMPLETE
    message = None
    try:
        transcribe_audio(audio_path, task_id, logger)
    except Exception as e:
        logger.error(str(e))
        status = TaskStatus.FAILED
        message = str(e)

    update_task(Task(
        id=task_id,
        status=status,
        message=message
    ))
