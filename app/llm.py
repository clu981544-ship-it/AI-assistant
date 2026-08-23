from openai import OpenAI

from app.config import (
    DEEPSEEK_API_KEY,
    BASE_URL,
    MODEL_NAME,
)


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=BASE_URL,
)


def chat(messages: list) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"API请求失败：{e}"