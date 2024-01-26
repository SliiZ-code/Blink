import os
import glob
import time
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from subtitles import srtToJson
from openai import OpenAI,AsyncOpenAI
import base64
import asyncio
from aiohttp import ClientSession
from skimage.filters import gaussian
from pytube import Playlist
import random
from PIL import Image,ImageFont
from pilmoji import Pilmoji
from emoji import emojize

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

def findEmojis(parts):
    wordsEmojis={}
    for part in parts :
        mots=part.split()
        for i in range(len(mots)-1):
            if mots[i+1]!=emojize(mots[i+1],language='alias'):
                wordsEmojis[mots[i]]=mots[i+1]
    return wordsEmojis

def removeEmojis(parts):
    script=[]
    for part in parts:
        mots=part.split()
        sentence=''
        for mot in mots:
            if mot.count(":")!=2:
                sentence+=mot+' '
        script.append(sentence)
    return script

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

def removePunctuation(word):
    word=word.replace(".","")
    word=word.replace('"',"")
    return word

parts=find_script(message)
for p in parts:
    print(emojize(p,language='alias'))
images_descriptions=find_images(message)
images_descriptions.pop(0)
emojis=findEmojis(parts)
print("emojis : ",emojis)
parts=removeEmojis(parts)

async def tti(session, input, i):
   print(f"Image {i+1} Generation")
   async with session.post(
       f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
       headers={
           "Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": f"Bearer {os.getenv('STABILITY_KEY')}"
       },
       json={
           "text_prompts": [
               {
                  "text": input
               }
           ],
           "height": 1344,
           "width": 768,
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

async def emojiGen(cle,emoji):
        print(f"Emoji {cle} Generation")
        emojiText=emojize(removePunctuation(emoji),language='alias')
        with Image.new('RGB', (150, 150), (0, 0, 0)) as emojiImage:
            font = ImageFont.truetype('arial.ttf', 24)
            with Pilmoji(emojiImage) as pilmoji:
                pilmoji.text((10, 10), emojiText.strip(), (0, 0, 0), font,emoji_scale_factor=3.5, emoji_position_offset=(0, 0))
        emojiImage.save(f"Temp/Emojis/emoji{removePunctuation(cle)}.png")

async def ImgAudioAndEmojiGen():
    async with ClientSession() as session:
        await asyncio.gather(*(tti(session, images_descriptions[i], i) for i in range(len(images_descriptions))),*(tts(parts[i],i) for i in range(len(parts))),*(emojiGen(cle,emoji) for cle,emoji in emojis.items()))

print("Generating images and audios")
startTimeImgAndAudios=time.time()

asyncio.run(ImgAudioAndEmojiGen())

endTimeImgAndAudios=time.time()
print("Images and Audios generated in ",endTimeImgAndAudios-startTimeImgAndAudios," seconds")
print("Generating the video")

startTimeVideo=time.time()
videos=[]

def zoom(t):
    max=0.2
    if t < max:
        return 1 + 0.6*t
    else:
        return 1 + 0.6*max

def blur(image):
    return gaussian(image.astype(float),sigma=8)

for i in range(len(parts)):
    if i==0:
        intro=ImageClip(f"Temp/Images/image{len(parts)-2}.png").set_audio(AudioFileClip(f"Temp/Audios/audio{i}.mp3")).set_duration(AudioFileClip(f"Temp/Audios/audio{i}.mp3").duration)
        intro.fps=1
        title=TextClip(txt=topic, font='Mont', fontsize=72,stroke_width=2,stroke_color='white',color='red',size=(768,1344),method='caption')
        title=title.set_start(0).set_duration(AudioFileClip(f"Temp/Audios/audio{i}.mp3").duration).set_position(("center","center"))
        blurredIntro=CompositeVideoClip([intro.fl_image(blur),title])
        videos.append(blurredIntro)
    elif i==len(parts)-1:
        final=ImageClip(f"Temp/Images/image{len(parts)-1}.png").set_audio(AudioFileClip(f"Temp/Audios/audio{i}.mp3")).set_duration(AudioFileClip(f"Temp/Audios/audio{i}.mp3").duration)
        final.fps=1
        videos.append(final.fl_image(blur))
    else :
        video = ImageClip(f"Temp/Images/image{i}.png").resize(zoom).set_audio(AudioFileClip(f"Temp/Audios/audio{i}.mp3")).set_duration(AudioFileClip(f"Temp/Audios/audio{i}.mp3").duration)
        video.fps=10
        videos.append(video)
        

final_clip = concatenate_videoclips(videos,method='compose')
final_clip=final_clip.fx(vfx.speedx,1.2)
final_clip.write_videofile(f"Temp/video.mp4")

endTimeVideo=time.time()
print("Video generated in",endTimeVideo-startTimeVideo," seconds")

print("Generating transcription")
startTimeTranscription=time.time()
audio_file = open(f"Temp/video.mp4", "rb")
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

print("Adding music")

pl=Playlist("https://youtube.com/playlist?list=OLAK5uy_kqnK3wLCL5Ro-J-IwkhsaYVszy1VC3e94&si=xyq4TmJw4RjPSSO6")
song=random.choice(pl.videos)
song.streams.first().download(filename="song.mp4",output_path="Temp")
video=VideoFileClip(f"Temp/video.mp4")
song=AudioFileClip("Temp/song.mp4").volumex(0.07).set_duration(video.duration)
audioWithMusic=CompositeAudioClip([video.audio,song])

video.audio=audioWithMusic

print("Generating subtitles")
startTimeSubstitles=time.time()

json=srtToJson("Temp/subtitles.srt")

newEmojis={}
for key,value in emojis.items():
    newEmojis[removePunctuation(key)]=removePunctuation(value)
emojis=newEmojis

subtitles_list=[]
subtitles_list.append(video)
for sentence in json:
    if sentence["startTime"]>0:
        subtitle=TextClip(txt=sentence["text"], font='Mont', stroke_width=2,stroke_color='black',color='white',size=(700,200),method='caption')
        subtitle=subtitle.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).margin(bottom=50, opacity=0).set_position(("center","bottom"))
        subtitles_list.append(subtitle)
    for word in sentence["text"].split():
        if removePunctuation(word) in emojis:
            print(word,emojize(emojis[removePunctuation(word)],language='alias'))
            image=ImageClip(f"Temp/Emojis/emoji{removePunctuation(word)}.png")
            image=vfx.mask_color(image,color=[0,0,0])
            image=image.set_start(sentence["startTime"]).set_duration((sentence["endTime"]-sentence["startTime"])).margin(bottom=200, opacity=0).set_position(("center","bottom"))
            subtitles_list.append(image)

subs=CompositeVideoClip(subtitles_list)

subs.write_videofile(f"{topic}.mp4")
endTime=time.time()
timer=endTime-startTime
print("Subtitles generated in",endTime-startTimeSubstitles," seconds")
print("[END]")
print("Generated in ",timer," seconds")