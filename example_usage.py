"""
Example: Using LLMClient with different providers
Demonstrates how to switch between Gemini and Qwen programmatically
"""

from src.utils.llm_client import LLMClient
import os
from dotenv import load_dotenv

load_dotenv()


def test_provider(provider_name: str):
    """Test a specific LLM provider"""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()} Provider")
    print('='*60)
    
    try:
        if provider_name == "gemini":
            client = LLMClient(
                api_key=os.getenv("GEMINI_API_KEY"),
                model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
                provider="gemini"
            )
        elif provider_name == "qwen":
            client = LLMClient(
                api_key=os.getenv("QWEN_API_KEY"),
                model_name=os.getenv("QWEN_MODEL", "qwen-plus"),
                provider="qwen"
            )
        else:
            print(f"Unknown provider: {provider_name}")
            return
        
        print(f"✓ Client initialized successfully")
        print(f"  Provider: {client.provider}")
        print(f"  Model: {client.model_name}")
        
        print("\nTest 1: Simple text generation")
        response = client.generate("What is an OKR? Answer in one sentence.", temperature=0.3)
        print(f"Response: {response}")
        
        print("\nTest 2: JSON generation")
        json_prompt = """List 3 example OKRs for a software engineering team.
        
Return as JSON with this structure:
{
  "okrs": [
    {
      "objective": "objective text",
      "key_results": ["kr1", "kr2", "kr3"]
    }
  ]
}"""
        json_response = client.generate_json(json_prompt, temperature=0.3)
        print(f"JSON Response: {json_response}")
        
        print("\nTest 3: Token counting")
        sample_text = "Improve customer satisfaction by 20% through enhanced support"
        token_count = client.count_tokens(sample_text)
        print(f"Token count for sample text: {token_count}")
        
        print(f"\n✅ All tests passed for {provider_name.upper()}!")
        
    except Exception as e:
        print(f"\n❌ Error testing {provider_name}: {str(e)}")
        print(f"   Make sure {provider_name.upper()}_API_KEY is set in .env")


def main():
    """Run tests for all configured providers"""
    print("LLM Provider Testing")
    print("="*60)
    
    provider = os.getenv("LLM_PROVIDER", "gemini")
    print(f"Current provider in .env: {provider}")
    
    print("\n" + "="*60)
    print("You can test each provider individually:")
    print("="*60)
    
    test_provider(provider)
    
    print("\n" + "="*60)
    print("To test the other provider:")
    print("="*60)
    print("1. Update LLM_PROVIDER in .env file")
    print("2. Make sure the corresponding API key is set")
    print("3. Run this script again")
    print("\nOr test both providers by calling:")
    print("  test_provider('gemini')")
    print("  test_provider('qwen')")


if __name__ == "__main__":
    main()
