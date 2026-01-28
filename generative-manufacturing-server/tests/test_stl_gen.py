
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stl_generator
from google import genai

load_dotenv()

async def test_generation():
    print("Testing STL generation...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in env.")
        return

    client = genai.Client(api_key=api_key)
    
    prompt = "A simple 10mm cube"
    filename = "test_cube"
    
    print(f"Prompt: {prompt}")
    
    # Run synchronous generator
    result = stl_generator.generate_model(prompt, filename, client)
    
    print("Result:", result)
    
    if result["status"] == "success" and os.path.exists(result["path"]):
        print(f"PASS: File generated at {result['path']}")
    else:
        print("FAIL: Generation failed.")

if __name__ == "__main__":
    asyncio.run(test_generation())
