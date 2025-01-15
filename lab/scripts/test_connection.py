import os
from openai import OpenAI


url = os.getenv("VLLM_HOST")
print("VLLM_HOST: %s", url)
key = os.getenv("VLLM_API_KEY")
print("VLLM_API_KEY: %s", key)
model = os.getenv("MODEL_NAME")
print("MODEL_NAME: %s", model)

client = OpenAI(
    base_url=url,
    api_key=key,
)

stream = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ],
)

print(stream)