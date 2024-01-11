import requests
import base64

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
                "text": "A lighthouse on a cliff"
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
