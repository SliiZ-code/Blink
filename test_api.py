from openai import OpenAI
import requests
client = OpenAI()

response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)
print(response)
# Save the file
with open(f"audiotest.mp3", "wb") as f:
    f.write(response.content)