import os
import requests
import glob
import time
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips
from openai import OpenAI
import base64

startTime=time.time()

client=OpenAI()

topic=input("Insert the subject of the top 5 video :")

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

def find_script(m):
    parts_list=[]
    part=""
    for c in m:
        if c=='\n':
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

for part in parts:
    print(part)


files = glob.glob('Images/*.png')
for f in files:
    os.remove(f)

files = glob.glob('Audios/*.mp3')
for f in files:
    os.remove(f)

files = glob.glob('Videos/*.mp4')
for f in files:
    os.remove(f)

print("Generating images")

for i in range(len(images_descriptions)):
    response = requests.post(
        f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer sk-EiUIrPeq0Pr3OmMUVJU2KKx4jyF6qVWdIw1m3a1r5AVlLv40"
        },
        json={
            "text_prompts": [
                {
                    "text": images_descriptions[i]
                }
            ],
            "height": 1024,
            "width": 1024,
            "steps": 30,
            "style-preset":"cinematic",
        },
    )
    data=response.json()

    with open(f"Images/image{i+1}.png","wb") as f:
        f.write(base64.b64decode(data["artifacts"][0]["base64"]))

print("Generating audios")

for i in range(len(parts)):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=parts[i]
        )
    # Save the file
    with open(f"Audios/audio{i}.mp3", "wb") as f:
        f.write(response.content)

print("Generating the video")

videos=[]

def add_static_image_to_audio(image_path, audio_path, output_path):
    """Create and save a video file to `output_path` after combining a static image that is located in `image_path` with an audio file in `audio_path`"""
    # create the audio clip object
    audio_clip = AudioFileClip(audio_path)

    # create the image clip object
    image_clip = ImageClip(image_path)

    # use set_audio method from image clip to combine the audio with the image
    video_clip = image_clip.set_audio(audio_clip)

    # specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio_clip.duration

    # set the FPS to 1
    video_clip.fps = 1

    # write the resulting video clip
    video_clip.write_videofile(output_path)

add_static_image_to_audio("image0.png","Audios/audio0.mp3","Videos/video0.mp4")
add_static_image_to_audio("Images/image1.png","Audios/audio1.mp3","Videos/video1.mp4")
add_static_image_to_audio("Images/image2.png","Audios/audio2.mp3","Videos/video2.mp4")
add_static_image_to_audio("Images/image3.png","Audios/audio3.mp3","Videos/video3.mp4")
add_static_image_to_audio("Images/image4.png","Audios/audio4.mp3","Videos/video4.mp4")
add_static_image_to_audio("Images/image5.png","Audios/audio5.mp3","Videos/video5.mp4")

videos=["Videos/video0.mp4","Videos/video1.mp4","Videos/video2.mp4","Videos/video3.mp4","Videos/video4.mp4","Videos/video5.mp4"]
video_clips=[VideoFileClip(file) for file in videos]
final_clip = concatenate_videoclips(video_clips)
final_clip.write_videofile(f"{topic}.mp4")

endTime=time.time()
timer=endTime-startTime
print("Generated in ",timer," seconds")
