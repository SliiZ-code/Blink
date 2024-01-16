import asyncio
from aiohttp import ClientSession
import requests
import time
import base64
import glob
import os


images_descriptions=["The Door to Hell in Turkmenistan surrounded by a barren desert landscape.","A majestic bird's-eye view of the Richat Structure in Mauritania, showcasing its intricate patterns.","A map highlighting the Bermuda Triangle, surrounded by a mysterious aura.","The Stone Forest in China with tall, slender limestone formations, resembling a mystical wonderland.","A stunning aerial view of the Great Blue Hole, with clear turquoise waters and the dark abyss beneath."]
async def tti(session, input, i):
   print(f"Image {i+1}")
   print(input)
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

async def imgGen():
   async with ClientSession() as session:
       await asyncio.gather(*(tti(session, images_descriptions[i], i) for i in range(len(images_descriptions))))

def stti(input,i):
    print(f"Image {i+1}")
    print(input)
    response = requests.post(
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
    )

    data=response.json()

    with open(f"v1_txt2img.png", "wb") as f:
        f.write(base64.b64decode(data["artifacts"][0]["base64"]))

def main():
    for i in range(len(images_descriptions)):
        stti(images_descriptions[i],i)

files = glob.glob('Temp/**/*')
for f in files:
    os.remove(f)

start=time.time()
asyncio.run(imgGen())
end=time.time()
print("Async",end-start)

files = glob.glob('Temp/**/*')
for f in files:
    os.remove(f)

start=time.time()
main()
end=time.time()
print("Classic",end-start)

