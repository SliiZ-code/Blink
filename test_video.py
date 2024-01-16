from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips
import time

print("Generating the video")

startTimeVideo=time.time()
videos=[]

def createVideoFromImageAndAudio(imagePath, audioPath):
    videoClip = ImageClip(imagePath).set_audio(AudioFileClip(audioPath)).set_duration(AudioFileClip(audioPath).duration)
    videoClip.fps=1
    return videoClip

for i in range(0,7):
    if i==0:
        videos.append(createVideoFromImageAndAudio("image0.png","Temp/Audios/audio0.mp3"))
    else :
        videos.append(createVideoFromImageAndAudio(f"Temp/Images/image{i}.png",f"Temp/Audios/audio{i}.mp3"))

print(type(videos[0]))
final_clip = concatenate_videoclips(videos)
final_clip.write_videofile(f"Temp/finalVideo.mp4")

endTimeVideo=time.time()
print("Video generated in",endTimeVideo-startTimeVideo," seconds")