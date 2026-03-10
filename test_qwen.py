import os
from openai import OpenAI
from dotenv import load_dotenv


def main():
    load_dotenv()

    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("QWEN_API_KEY environment variable is not set.")
        return

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        response = client.chat.completions.create(
            model=os.getenv("QWEN_MODEL", "qwen-plus"),
            messages=[{"role": "user", "content": "Reply with the single word: OK"}]
        )
        
        print("Request succeeded. Model response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Request failed. Error was:")
        print(repr(e))


if __name__ == "__main__":
    main()
