import os
import pyautogui
from PIL import Image

def test_environment():
    print("--- Step 1 Verification ---")
    
    # 1. Test Screen Dimensions
    width, height = pyautogui.size()
    print(f"Success: Screen Resolution Detected: {width}x{height}")
    
    # 2. Test Safe Mouse Movement
    print("Moving mouse to (100, 100) over 1 second...")
    pyautogui.moveTo(100, 100, duration=1.0)
    print("Success: Mouse moved.")
    
    # 3. Test Desktop Screenshot Capture
    print("Capturing screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot_path = "current_screen.png"
    screenshot.save(screenshot_path)
    
    if os.path.exists(screenshot_path):
        print(f"Success: Saved screenshot to disk.")
        with Image.open(screenshot_path) as img:
            print(f"Image verification: Format={img.format}, Size={img.size}")
    else:
        print("Error: Failed to save screenshot.")

if __name__ == "__main__":
    test_environment()
