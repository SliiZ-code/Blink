from openai import OpenAI
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from subtitles import srtToJson
client = OpenAI()


print("Generating transcription")

audio_file = open("top 5 dog breeds.mp4", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  language="en",
  response_format="srt",
)


with open("subtitles.srt", "w") as f:
        f.write(transcript)

json=srtToJson("subtitles.srt")

subtitles_list=[]
subtitles_list.append(VideoFileClip("top 5 dog breeds.mp4"))
for sentence in json:
        subtitle=TextClip(txt=sentence["text"], font='Georgia-Regular', fontsize=24, color='white')
        subtitle=subtitle.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).set_pos(("center","center"))
        subtitles_list.append(subtitle)

subs=CompositeVideoClip(subtitles_list)

subs.write_videofile("test_subs.mp4",fps=24)