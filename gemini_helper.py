import os
import json
import requests
from datetime import datetime

def configure_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY environment variable is not set. Please configure your API key in the Secrets.")
    return api_key

def log_prompt(prompt: str):
    os.makedirs("prompts", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = f"prompts/prompt_{timestamp}.txt"
    with open(log_file_path, "w") as log_file:
        log_file.write(prompt)

def analyze_with_rest_api(prompt: str, api_key: str) -> str:
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            return "Error: No valid response from AI model"
        
        except requests.exceptions.HTTPError as e:
            last_error = e
            if e.response.status_code != 404:
                raise Exception(f"API request failed: {str(e)}")
            continue
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    raise Exception(f"All models failed. Last error: {str(last_error)}. Please verify your API key is valid and has access to Gemini models.")

def analyze_brd_and_patch(brd_content: str, patch_content: str) -> str:
    api_key = configure_gemini()
    
    system_instruction = """You are a technical analyst helping developers understand feature implementations.
Your task is to analyze a BRD (Business Requirements Document) or User Story and a code patch file, then generate a comprehensive analysis document.

The analysis should include:
1. **Feature Overview**: Summarize the feature from the BRD in simple terms
2. **Technical Changes**: Explain what changes were made in the patch
3. **Implementation Mapping**: How the code changes implement the BRD requirements
4. **Files Modified**: List all files changed with brief descriptions
5. **Key Functions/Methods**: Important code elements added or modified
6. **Implementation Guide**: Step-by-step guide for implementing this feature in the latest branch
7. **Considerations**: Any edge cases, dependencies, or important notes

Format the response in clean, well-structured Markdown."""

    prompt = f"""
{system_instruction}

BRD/User Story Content:
---
{brd_content}
---

Patch File Content:
---
{patch_content}
---

Please analyze the above and generate a comprehensive analysis document following the structure outlined.
"""

    log_prompt(prompt)

    return analyze_with_rest_api(prompt, api_key)
