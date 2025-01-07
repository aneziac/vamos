import whisper

model = whisper.load_model("turbo")
result = model.transcribe("../data/accent_guy.mp3")
print(result["text"])
