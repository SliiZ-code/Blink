from openai import OpenAI
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from subtitles import srtToJson
import time
client = OpenAI()


print("Generating transcription")
start=time.time()
audio_file = open("top 5 best European countries.mp4", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  language="en",
  response_format="srt",
)

with open("subtitles.srt", "w") as f:
        f.write(transcript)

end=time.time()
print(end-start)