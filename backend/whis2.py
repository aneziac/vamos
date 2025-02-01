import whisper

def transcribe_with_whisper(input_file, output_dir):
    # could be base/small/medium 
    model = whisper.load_model("base")
    
    result = model.transcribe(
        input_file,
        language="en",
        word_timestamps=True,
    )
    
    #transcribed_text = result["text"]
    segments = result["segments"]

    srt_file = f"{output_dir}/output.srt"
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
    
    print(f"Transcription saved to: {srt_file}")
    #print(transcribed_text)
    #print(segments)

input_audio_file = "audio.mp3"
output_directory = "/Users/aq2003/vam"
transcribe_with_whisper(input_audio_file, output_directory)