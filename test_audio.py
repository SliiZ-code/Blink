from openai import AsyncOpenAI
import asyncio
import time

client=AsyncOpenAI()

parts=["Hello everyone, welcome to the top 5 strangest places on the planet","Number 5: The Door to Hell in Turkmenistan. Imagine a vast crater filled with fiery flames that have been burning for over four decades. This mesmerizing sight is not a fictional hell, but a natural gas field in Derweze, Turkmenistan.","Number 4: The Richat Structure in Mauritania. Known as the 'Eye of the Sahara,' this geological marvel is a circular formation that can only be fully appreciated from space. The concentric rings of rock and sand create a stunning and perplexing sight.","Number 3: The Bermuda Triangle. This infamous stretch of sea, located between Miami, Bermuda, and Puerto Rico, has sparked countless myths and mysteries. Numerous disappearances of ships and planes have occurred within its boundaries, leaving experts baffled.","Number 2: The Stone Forest in China. Embark on a journey through a whimsical landscape of towering limestone pillars. Formed by centuries of erosion, this otherworldly forest in Yunnan Province will transport you to a surreal realm.","And finally, Number 1: The Great Blue Hole in Belize. Dive into the depths of an underwater sinkhole that reveals a mesmerizing world below the surface. This giant marine sinkhole boasts vibrant corals, unique rock formations, and a plethora of marine life."]
async def tts(input,i):
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input
        )
    # Save the file
    with open(f"Temp/Audios/audio{i}.mp3", "wb") as f:
        f.write(response.content)

start=time.time()

async def main():
    await asyncio.gather(*(tts(parts[i],i) for i in range(0,6)))

asyncio.run(main())
end=time.time()

print(end-start,"seconds")