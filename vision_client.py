import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Automatically load the credentials from your local .env file
load_dotenv()

def encode_image_to_base64(image_path):
    """Converts a local image file into a base64 string for API transmission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_screen_layout(image_path, user_instruction, history=None):
    """Sends the screen image, user instruction, and past action history to Meta's Muse Wonder API."""
    
    api_key = os.environ.get("META_API_KEY")
    if not api_key:
        raise ValueError("Missing META_API_KEY environment variable in your .env file!")
        
    # Standard OpenAI initialization pointing directly to the official Meta base endpoint
    client = OpenAI(
        base_url="https://api.meta.ai/v1",
        api_key=api_key
    )
    
    base64_image = encode_image_to_base64(image_path)

    # Convert the running execution history list into a readable sequence block
    history_str = ""
    if history and len(history) > 0:
        history_str = "\nACTIONS ALREADY EXECUTED IN PREVIOUS STEPS LOG:\n" + "\n".join(history)

    system_prompt = (
        "You are an advanced cross-platform OS automation engine. Analyze the provided screenshot.\n"
        "Identify the exact coordinate location of the UI element requested by the user.\n"
        "CRITICAL STATE CHECK: Evaluate if the user's overall goal, or the current sub-step of their goal, "
        "has already been accomplished based on the screenshot and the history of actions already executed.\n"
        "Use the provided history to determine if you have already triggered a specific state transition, "
        "and always advance forward toward completing the rest of the user's objective.\n"
        f"{history_str}\n"
        "CRITICAL BOUNDARIES: Your coordinate system MUST use a normalized grid from 0 to 1000.\n"
        "Top-left corner is x=0, y=0. Bottom-right corner is x=1000, y=1000.\n"
        "Respond ONLY with a valid JSON object matching one of these formats:\n"
        "{\"action\": \"click\", \"x\": normalized_x, \"y\": normalized_y} or\n"
        "{\"action\": \"type\", \"text\": \"text_here\"} or\n"
        "{\"action\": \"press_key\", \"key\": \"key_name\"} or\n"
        "{\"action\": \"scroll_down\"} or\n"
        "{\"action\": \"intercept\", \"reason\": \"clear description of user selection choice needed\"} or\n"
        "{\"action\": \"done\"}\n"
        "Do not include any conversational explanation, text filler, or markdown code blocks."
    )


    # Calling the correct official /v1/chat/completions endpoint
    response = client.chat.completions.create(
        model="muse-wonder-1.0",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"System Task Context:\n{system_prompt}\n\nUser Requested Goal: {user_instruction}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.0
    )
    
    # Extract response text using the correct message content attribute map
    return response.choices[0].message.content.strip()



if __name__ == "__main__":
    print("--- Step 2: Testing Cloud Meta Muse Wonder Pipeline ---")
    try:
        test_image = "current_screen.png"
        sample_prompt = "Find the terminal section or a window button."
        
        print("Sending screen frame to Meta Model API clusters...")
        ai_response = analyze_screen_layout(test_image, sample_prompt)
        
        print("\n=== Meta Model Output ===")
        print(ai_response)
        print("=========================")
        print("Success: Meta cloud vision inference working perfectly!")
        
    except Exception as e:
        print(f"\nCloud Execution Error: {e}")
