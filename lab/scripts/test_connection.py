import os
from openai import OpenAI


client = OpenAI(
    base_url="http://vllm-server:9999/v1",
    api_key="12345",
)

stream = client.chat.completions.create(
    model="Breeze-7B",
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