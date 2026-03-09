import os
from google import genai
from dotenv import load_dotenv


def main():
    # Load environment variables from .env if present
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable is not set.")
        return

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Reply with the single word: OK"
        )
        print("Request succeeded. Model response:")
        print(response.text)
    except Exception as e:
        print("Request failed. Error was:")
        print(repr(e))


if __name__ == "__main__":
    main()

