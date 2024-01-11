from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, concatenate_videoclips

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

add_static_image_to_audio("image0.png","Audios/audio1.mp3","video0.mp4")
add_static_image_to_audio("Images/image1.png","Audios/audio2.mp3","video1.mp4")
add_static_image_to_audio("Images/image2.png","Audios/audio3.mp3","video2.mp4")
add_static_image_to_audio("Images/image3.png","Audios/audio4.mp3","video3.mp4")
add_static_image_to_audio("Images/image4.png","Audios/audio5.mp3","video4.mp4")

videos=["video0.mp4","video1.mp4","video2.mp4","video3.mp4","video4.mp4"]
video_clips=[VideoFileClip(file) for file in videos]
final_clip = concatenate_videoclips(video_clips)
final_clip.write_videofile("videoFinal.mp4")