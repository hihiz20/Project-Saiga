# Project Saiga: An Interactive Muti-Modal AI Agent built with Meta Muse Models

Project Saiga is a hands-free interactive Multi-Modal AI Agent that allows control over the keyboard and mouse. Saiga works by waiting and listening for the user's command and takes that command to perform sequential desktop actions inside the user’s computer operating system (Windows or macOS) by moving the cursor or typing. The project aims to help individuals with daily automation whenever they need an extra hand. Saiga not only focuses on daily task automation but aids seniors who are having a hard time navigating the operating system including those with disabilities and hand arthritis to reduce pain. Saiga can perform actions like opening a new tab, writing an email, online shopping, help book reservations, or help users with some tasks without having to constantly copy-pasting back and forth into web-browser sidebars just to parse your screen


## 🚀 Core Capabilities
- **Real-Time Voice Streaming:** Orchestrates real-time audio-to-text pipelines utilizing Websockets and Asyncio for ultra-low latency transcription.
- **Vision-Driven Desktop Automation:** Processes display context using multi-modal capabilities to identify UI elements, map screen coordinates, and execute precise mouse and keyboard actions.
- **Accessibility Optimization:** Eliminates traditional typing and complex physical peripheral interactions by converting natural voice instructions into reliable macro sequences.

---

## 📂 Project Structure & Module Breakdown
*Click on any file below to see its technical implementation details:*

<details>
<summary>📂 <b>agent_orchestrate.py</b> (The Orchestration Brain)</summary>
<br>
This is the brain of Saiga. It allows the agent to fully interact with the user’s operating system by connecting all the separate scripts (audio and vision) together into a single automated execution loop. It captures the user's voice command, translates that request from audio to text, captures a screenshot of the user’s computer screen, sends that image to the vision model, and calculates the map of the coordinates directly to the screen resolution so PyAutoGUI can move the cursor and click on the exact UI element.
</details>

<details>
<summary>📂 <b>audio_client.py</b> (Muse Voice Transcribe 1.0)</summary>
<br>
Implements the <code>muse-voice-transcribe-1.0</code> pipeline that allows Saiga to capture real-time audio-to-text for processing user commands. It provides live captures and ultra-fast real-time chunking at approximately 12 chunks per second. Instead of recording and storing the audio internally, it opens a live WebSocket connection tunnel directly to Meta’s servers. Additionally, it utilizes an <code>asyncio.Queue</code> to queue up bytes from the microphone onto a virtual conveyor belt, allowing the script to stream raw audio continuously to the server without freezing or dropping words if the internet connection fluctuates.
</details>

<details>
<summary>📂 <b>vision_client.py</b> (Muse Wonder 1.0)</summary>
<br>
Gives Saiga the ability to see what is on the user’s screen by converting the image into a binary format through a base64 encoding process, allowing this data to send requests to the backend through web protocols. A vital part of Saiga’s vision is using a normalized 0-1000 coordinate grid and checking if the task is already completed to avoid unnecessary repetitive requests to the server, saving bandwidth. To ensure Saiga is consistent in generating coordinates rather than guessing creatively, the <code>temperature=0.0</code> parameter is enforced. Powered by Meta’s Muse Wonder 1.0 for state-of-the-art multimodal reasoning.
</details>

<details>
<summary>📂 <b>test_system.py</b> (Low-Level Verification Utility)</summary>
<br>
A standalone verification utility designed to ensure that the host operating system allows PyAutoGUI and Pillow to capture screen pixels and move the cursor. Whenever Saiga is deployed to a brand new user, this isolated test file checks for permissions, ensures PyAutoGUI and Pillow are correctly installed inside the local Python virtual environment, and proves that Python can communicate with the hardware hooks independently.
</details>

---

## 🛠️ System Architecture & Phase Breakdown

<details>
<summary>🗺️ <b>System Architecture Flowchart</b></summary>
<br>
Here is the end-to-end data pipeline from voice capture to mouse automation:
<br><br>
<i>[Drag and drop your Architecture Design flowchart image here]</i>
</details>

<details>
<summary>⏱️ <b>Phase 1: Low-Level OS Integration</b></summary>
<br>
In order to build the complete working project. I first have to break down each step by laying the foundation first then build my way up from there. Another important thing when laying a foundation is to make sure that the foundation I set will be used consistently through the project. Constant adjustments especially in large projects can affect further phases and how it functions. The main objective of this phase is to establish low-level system hooks to verify python runtime can safely control inputs and capture screen data across both macOS and Windows environments. I will establish two foundational tech stacks: Pyautogui and Pillow.<br>

The primary challenge in phase 1 was figuring out how to programmatically move the mouse and take a screenshot after it moved to or landed in that specific input coordinates (x,y). This was solved by integrating two specialized Python libraries: PyAutoGUI (to programmatically drive system mouse inputs) and Pillow (to handle real-time frame capture and processing). 
Moving into the second phase, the next step is to give Saiga the ear to capture real-time audio and stream it to Muse Voice Transcribe 1.0 model to process into text.

The execution flow begins at the Software Layer, which leverages Python libraries to abstract complex actions into simple commands. Because Python cannot talk to hardware directly, these commands pass down to the OS API Layer. This layer acts as the system gatekeeper – requesting native permissions from Windows or macOS to interact with the system hooks, verifying accessibility access, and safely bridging the gap between your code and the underlying drivers. Once permission is granted, the request passes into the Kernel Layer, which acts as the core operating system bridge to communicate with system drivers. The kernel routes these instructions directly to the specific mouse and graphics drivers running in the system background. Finally, the Hardware Layer receives these low-level system commands, instantly translating the raw digital instructions into physical actions – updating the cursor position on your monitor and reading the raw pixels from your video memory grid.

<br><br>
<i>[Drag and drop your Phase 1 diagram image here]</i>
</details>

<details>
<summary>🗣️ <b>Phase 2: Implementing WebSockets & Asyncio for Real-Time Audio-to-Text</b></summary>
<br>
Gives Saiga the ability to hear user requests in real-time. This works by implementing WebSockets, asyncio, and Muse Voice Transcribe 1.0 to provide highly accurate, low-latency, and fast audio-to-text concurrency management, ensuring the main execution thread remains non-blocking while streaming real-time audio data chunks.
<br><br>
<i>[Drag and drop your Phase 2 diagram image here]</i>
</details>

<details>
<summary>👁️ <b>Phase 3: Multimodal Vision Pipeline (Muse Wonder 1.0)</b></summary>
<br>
Allows Saiga to see what is on the user's screen before taking action. To resolve model hallucination across screen pixel grids, the system prompt injects absolute bounding-box constraints (0-1000 grid rules) and sets <code>temperature=0.0</code> to target the exact UI elements requested by the user.
<br><br>
<i>[Drag and drop your Phase 3 diagram image here]</i>
</details>

---
*Developed as a solo indie project for the Meta Cerebral Valley Hackathon 2026. Built with a commitment to clean system architecture and meaningful digital accessibility.*
