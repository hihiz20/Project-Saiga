# Project Saiga: An Interactive Muti-Modal AI Agent built with Meta Muse Models

Project Saiga is a hands-free, multi-modal desktop automation agent built for the Meta Global AI Developer Hackathon. By combining real-time audio transcription pipelines with computer vision orchestration, Saiga bridges digital accessibility gaps—allowing individuals with mobility constraints, hand arthritis, or elderly users to fully control their desktop environment using intuitive voice commands.

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
The main objective of this phase is to establish low-level system hooks to verify the Python runtime can safely control inputs and capture screen data across both macOS and Windows environments. Built using PyAutoGUI (to programmatically drive system mouse inputs) and Pillow (to handle real-time frame capture and processing).
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
