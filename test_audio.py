import requests

headers = {
    'Authorization': 'Bearer md-bYjgEKHCOoecvBYmtzIHTavyvfWdAIPqMrRdEcKXZmFGhVwS'
}

data = {
    "text": "Hello everyone, welcome to the top 5 richest men on Earth.Hello everyone, welcome to the top 5 richest men on Earth.Hello everyone, welcome to the top 5 richest men on Earth.Hello everyone, welcome to the top 5 richest men on Earth.Hello everyone, welcome to the top 5 richest men on Earth.Hello everyone, welcome to the top 5", # This is required
    "voice_id": "pNInz6obpgDQGcFmaJgB" # This is optional
}

response = requests.post("https://api.mandrillai.tech/v1/audio/tts",
                         json=data,
                         headers=headers)

print(response)