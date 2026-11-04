import json
import re
import time
import os
import subprocess
import pyautogui
from vision_client import analyze_screen_layout
from audio_client import listen_for_command
from openai import OpenAI

# Core Configuration: Disable PyAutoGUI's automatic corner panic crash
pyautogui.FAILSAFE = False

# The exact physical logical size my Mac reports to PyAutoGUI
MAC_WIDTH = 1710
MAC_HEIGHT = 1107


def translate_saiga_response(target_text, original_user_audio):
#Leverages the Meta API to automatically translate Saiga's status feedback phrases 
# into the exact native language spoken by the user with zero hardcoding.    
    api_key = os.environ.get("META_API_KEY")
    if not api_key:
        return target_text # Fallback to original text if no key found
        
    client = OpenAI(base_url="https://meta.ai", api_key=api_key)
    
    system_prompt = (
        "You are Saiga's internal voice localization module.\n"
        "Translate the provided system phrase into the exact same language as the user's audio transcription text.\n"
        "Maintain a helpful, friendly assistant tone.\n"
        "Respond ONLY with the translated text string. Do not include markdown or explanations."
    )
    
    try:
        response = client.chat.completions.create(
            model="muse-wonder-1.0",
            messages=[
                {
                    "role": "user",
                    "content": f"System Prompt Context: {system_prompt}\n\nSystem phrase to translate: '{target_text}'\nUser's spoken text sample: '{original_user_audio}'"
                }
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation bridge warning: {e}")
        return target_text # Fallback cleanly to English if network fails


def set_mac_microphone_volume(volume_level):
    """Uses macOS native AppleScript to physically change the hardware microphone input volume."""
    try:
        script = f"set volume input volume {volume_level}"
        subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Hardware Input Level Adjustment Warning: {e}")

def say_text_locally(text, speech_duration=0.5):
# Completely autonomous multilingual voice engine.
# Automatically detects non-English text characters and pairs them with 
# the native macOS voice engine profile seamlessly.
# Needs progress. The keyboard input doesn't work. DIdn't have time to fix it.
    print(f"[Saiga Voice]: '{text}'")
    
    set_mac_microphone_volume(0)
    time.sleep(0.1)
    
    # Default fallback voice profile (English)
    system_voice = "Samantha"
    
    # AUTONOMOUS CHARACTER DETECTION (No manual mapping required!)
    # Check for Japanese characters (Hiragana, Katakana, Kanji)
    if re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', text):
        system_voice = "Kyoko"
    
    # Check for native accent variations or specific structural words contextually
    else:
        text_lower = text.lower()
        # Spanish marker detection
        if any(w in text_lower for w in ["hola", "correo", "entendido", "tarea", "menú"]):
            system_voice = "Monica"
        # Indonesian marker detection
        elif any(w in text_lower for w in ["halo", "tugas", "selesai", "bisa", "buka"]):
            system_voice = "Damayanti"

    # Execute and block until the native voice profile finishes speaking
    subprocess.run(["say", "-v", system_voice, text])
    
    time.sleep(speech_duration)
    set_mac_microphone_volume(75)


# Cleans raw text
def parse_json_safely(raw_output):
    try:
        clean_text = re.sub(r'```(?:json)?\n?|\n?```', '', raw_output).strip()
        json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(0)
        clean_text = clean_text.replace("'", '"')
        return json.loads(clean_text)
    except Exception as e:
        print(f"Error parsing model output to JSON: {e}")
        return None

def execute_agent_loop(user_instruction, safety_cutoff=25):
    # 1. Automatically localize the opening phrase
    start_phrase = translate_saiga_response("Understood. Executing request.", user_instruction)
    say_text_locally(start_phrase, speech_duration=2.0)
    
    action_history = []
    step = 0
    
    while True:
        step += 1
        print(f"\n--- Dynamic Step {step} ---")
        
        if step > safety_cutoff:
            print(f"Safety Halt: Maximum loop ceiling reached.")
            stop_phrase = translate_saiga_response("I reached my safety execution ceiling. Pausing task.", user_instruction)
            say_text_locally(stop_phrase, speech_duration=3.5)
            break

        time.sleep(2.0) 
        
        screenshot_path = "current_screen.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        raw_ai_response = analyze_screen_layout(screenshot_path, user_instruction, history=action_history)
        action_package = parse_json_safely(raw_ai_response)
        
        if not action_package:
            print("Execution Halted: Could not parse vision payload.")
            break
            
        action_type = action_package.get("action", "").lower()
        print(f"-> Intended Action Decision: {action_type.upper()}")
        
        if action_type == "done":
            # 2. Automatically localize the completion phrase
            done_phrase = translate_saiga_response("Task completed.", user_instruction)
            say_text_locally(done_phrase, speech_duration=3.5)
            return True

        elif action_type == "intercept":
            reason_msg = action_package.get("reason", "Your decision is required.")
            print(f"[User Intercept Triggered]: {reason_msg}")
            
            # 3. Automatically localize the intercept request
            intercept_phrase = translate_saiga_response(f"Hey bro, I need your input here: {reason_msg}. Please tell me your choice.", user_instruction)
            say_text_locally(intercept_phrase, speech_duration=4.0)
            
            print("🎤 [Active Listen] Waiting for user choice selection...")
            user_choice = listen_for_command()
            
            if user_choice and len(user_choice.strip()) > 0:
                print(f"User selected preference choice: '{user_choice}'")
                action_history.append(f"Step {step}: Intercepted for user preference. User chose: '{user_choice}'")
                user_instruction = f"{user_instruction} (User selected choice: {user_choice})"
                continue
            else:
                print("No clear response captured. Halting for safety.")
                break

        elif action_type == "scroll_down":
            print("Executing Layout Navigation: Scrolling page view down...")
            pyautogui.scroll(-7)
            action_history.append(f"Step {step}: Scrolled down the page view to find more options.")
            continue

        elif action_type == "click":
            norm_x = action_package.get("x")
            norm_y = action_package.get("y")
            
            if norm_x is None or norm_y is None:
                print("Error: Missing coordinate properties.")
                break
                
            scaled_x = int((norm_x / 1000.0) * MAC_WIDTH)
            scaled_y = int((norm_y / 1000.0) * MAC_HEIGHT)
            
            print(f"Executing Click: Moving cursor to physical coordinates ({scaled_x}, {scaled_y})")
            pyautogui.moveTo(scaled_x, scaled_y, duration=1.0)
            pyautogui.click(clicks=1, interval=0.25)
            
            action_history.append(f"Step {step}: Clicked coordinates ({norm_x}, {norm_y})")
            
        elif action_type == "type":
            text_to_type = action_package.get("text", "")
            print(f"Executing Input: Typing text: '{text_to_type}'")
            pyautogui.write(text_to_type, interval=0.04)
            
            time.sleep(0.5)
            print("Executing Submission Fallback: Pressing 'enter'")
            pyautogui.press("enter")
            
            action_history.append(f"Step {step}: Typed text '{text_to_type}' and submitted field with enter key.")

        elif action_type == "press_key":
            key_target = action_package.get("key", "")
            print(f"Executing Key Trigger: Pressing '{key_target}'")
            pyautogui.press(key_target)
            
            action_history.append(f"Step {step}: Pressed system key '{key_target}'")
            
        time.sleep(1.5)

    return False



if __name__ == "__main__":
    print("=== 🌟 Saiga Conversational Agent Active ===")
    
    set_mac_microphone_volume(75)
    #say_text_locally("This is Saiga.", speech_duration=2.5)
    
    while True:
        print("\n[Passive Listen] Waiting for wake phrase or command...")
        spoken_phrase = listen_for_command().strip()
        
        if not spoken_phrase:
            continue
            
        print(f"[Detected Audio Feed]: '{spoken_phrase}'")
        spoken_lower = spoken_phrase.lower()
        
        # Check Condition A: User used the wake word explicitly
        if "saiga" in spoken_lower:
            say_text_locally("Yes. How can I help you with today?", speech_duration=2.2)
            
            print("🎤 [Active Listen] Grabbing user action instructions...")
            clean_instruction = listen_for_command()
            
            if clean_instruction and len(clean_instruction.strip()) > 0:
                print(f"Received Target Goal: '{clean_instruction}'")
                execute_agent_loop(clean_instruction)
                print("Flushing environment buffer...")
                time.sleep(1.0)
            else:
                say_text_locally("I didn't catch that instruction. Waiting for next command.", speech_duration=3.5)
                
        else:
            is_valid_command = False
            
            # 1. Instant Japanese verb triggers
            if re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', spoken_phrase) and any(w in spoken_phrase for w in ["開い", "書い", "検索", "クリック", "タイプ"]):
                is_valid_command = True
            
            # 2. Instant English structural intent triggers
            elif any(w in spoken_lower for w in ["write", "open", "book", "search", "find", "click", "type", "go to", "email", "show"]):
                is_valid_command = True
                
            # 3. Cloud Fallback: Use the Meta API if it's a completely new language
            else:
                api_key = os.environ.get("META_API_KEY")
                if api_key:
                    try:
                        client = OpenAI(base_url="https://meta.ai", api_key=api_key)
                        intent_check = client.chat.completions.create(
                            model="muse-wonder-1.0",
                            messages=[
                                {
                                    "role": "user",
                                    "content": (
                                        "Analyze if the following spoken phrase is an actionable computer automation command "
                                        "in any language.\n"
                                        "Respond with ONLY the word 'YES' if it is an actionable command, or 'NO' if it is just noise.\n"
                                        f"User Spoken Phrase: '{spoken_phrase}'"
                                    )
                                }
                            ],
                            temperature=0.0
                        )
                        decision = intent_check.choices[0].message.content.strip().upper()
                        if "YES" in decision:
                            is_valid_command = True
                    except Exception as e:
                        print(f"Intent check network fallback warning: {e}")

            # Routing Engine execution step
            if is_valid_command:
                print(f"Direct Intent Matched! Target Goal: '{spoken_phrase}'")
                execute_agent_loop(spoken_phrase)
                print("Flushing environment buffer...")
                time.sleep(1.0)
            else:
                print("Ambient audio filtered. Spoken phrase did not match an execution intent.")
            
        time.sleep(0.5)



