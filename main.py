import os
import requests
import glob
import time
from moviepy.editor import *
from subtitles import srtToJson
from openai import OpenAI,AsyncOpenAI
import base64
import asyncio
from aiohttp import ClientSession

client=OpenAI()
asyncClient=AsyncOpenAI()

topic=input("Insert the subject of the top [X] video : ")

files = glob.glob('Temp/**/*')
for f in files:
    os.remove(f)

startTime=time.time()
startTimeMessage=time.time()

print("Generating the message")

prompt=open("prompts.txt","r")
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt.read(),
        },
        {
            "role": "user",
            "content":f"Your topic is {topic}",
        }
    ],
    model="gpt-3.5-turbo",
)
message=chat_completion.choices[0].message.content
endTimeMessage=time.time()
print("Message generated in ",endTimeMessage-startTimeMessage," seconds")

def find_script(m):
    parts_list=[]
    part=""
    for c in m:
        if c=='\n':
            if len(part)>0:
                parts_list.append(part)
                part=""
        elif c=='[':
            return parts_list
        else:
            part+=c

def find_images(m):
    list=[]
    is_image=False
    image=""
    for c in m:
        if c==']':
            is_image=False
            list.append(image)
            image=""
        if is_image==True:
            image+=c
        if c=='[':
            is_image=True
    return list

parts=find_script(message)
images_descriptions=find_images(message)
images_descriptions.pop(0)

async def tti(session, input, i):
   print(f"Image {i+1} Generation")
   async with session.post(
       f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
       headers={
           "Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": f"Bearer sk-FC0cbjbZrG2msn2JWMsBPxdxgh3tSwJZz5O6joYcQZKcSkiq"
       },
       json={
           "text_prompts": [
               {
                  "text": input
               }
           ],
           "height": 1024,
           "width": 1024,
           "steps": 30,
           "style-preset":"cinematic",
       },
   ) as response:
       data = await response.json()

       with open(f"Temp/Images/image{i+1}.png","wb") as f:
           f.write(base64.b64decode(data["artifacts"][0]["base64"]))

async def tts(input,i):
    print(f"Audio {i} Generation")
    response = await asyncClient.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input
        )
    # Save the file
    with open(f"Temp/Audios/audio{i}.mp3", "wb") as f:
        f.write(response.content)

async def ImgAndAudioGen():
    async with ClientSession() as session:
        await asyncio.gather(*(tti(session, images_descriptions[i], i) for i in range(len(images_descriptions))),*(tts(parts[i],i) for i in range(len(parts))))

print("Generating images and audios")
startTimeImgAndAudios=time.time()

asyncio.run(ImgAndAudioGen())

endTimeImgAndAudios=time.time()
print("Images and Audios generated in ",endTimeImgAndAudios-startTimeImgAndAudios," seconds")
print("Generating the video")

startTimeVideo=time.time()
videos=[]

def createVideoFromImageAndAudio(imagePath, audioPath):
    videoClip = ImageClip(imagePath).set_audio(AudioFileClip(audioPath)).set_duration(AudioFileClip(audioPath).duration)
    videoClip.fps=1
    return videoClip

for i in range(len(parts)):
    if i==0:
        videos.append(createVideoFromImageAndAudio("image0.png","Temp/Audios/audio0.mp3"))
    else :
        videos.append(createVideoFromImageAndAudio(f"Temp/Images/image{i}.png",f"Temp/Audios/audio{i}.mp3"))

print(type(videos[0]))
final_clip = concatenate_videoclips(videos)
final_clip.write_videofile(f"Temp/Video.mp4")

endTimeVideo=time.time()
print("Video generated in",endTimeVideo-startTimeVideo," seconds")

print("Generating transcription")
startTimeTranscription=time.time()
audio_file = open(f"Temp/Video.mp4", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  language="en",
  response_format="srt",
)


with open("Temp/subtitles.srt", "w") as f:
        f.write(transcript)

endTimeTranscription=time.time()
print("Transcription generated in ",endTimeTranscription-startTimeTranscription," seconds")

print("Generating subtitles")
startTimeSubstitles=time.time()

json=srtToJson("Temp/subtitles.srt")

subtitles_list=[]
subtitles_list.append(VideoFileClip(f"Temp/Video.mp4"))
for sentence in json:
        if len(sentence["text"])<45:
            subtitle=TextClip(txt=sentence["text"], font='Mont', fontsize=42, stroke_width=3,stroke_color='black',color='red',bg_color='white')
            subtitle=subtitle.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).margin(bottom=50, opacity=0).set_position(("center","bottom"))
            subtitles_list.append(subtitle)
        else :
            sub1=sentence["text"][0:len(sentence["text"])//2]
            sub2=sentence["text"][len(sentence["text"])//2:len(sentence["text"])]
            subtitle1=TextClip(txt=sub1, font='Mont', fontsize=42, stroke_width=3,stroke_color='black',color='red',bg_color='white')
            subtitle1=subtitle1.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).margin(bottom=100, opacity=0).set_position(("center","bottom"))
            subtitles_list.append(subtitle1)
            subtitle2=TextClip(txt=sub2, font='Mont', fontsize=42, stroke_width=3,stroke_color='black',color='red',bg_color='white')
            subtitle2=subtitle2.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).margin(bottom=50, opacity=0).set_position(("center","bottom"))
            subtitles_list.append(subtitle2)

subs=CompositeVideoClip(subtitles_list)

subs.write_videofile(f"{topic}.mp4")
endTime=time.time()
timer=endTime-startTime
print("Subtitles generated in",endTime-startTimeSubstitles," seconds")
print("[END]")
print("Generated in ",timer," seconds")