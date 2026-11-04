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
<img width="3288" height="8191" alt="Muse Voice Vision Automation Pipeline-2026-11-04-004031" src="https://github.com/user-attachments/assets/f3715369-4cda-4d72-9c3d-b3d30e79c021" />
<br>
<br>
</details>


<details>
<summary>⏱️ <b>Phase 1: Low-Level OS Integration</b></summary>
<br>

In order to build the complete working project, I first have to break down each step by laying the foundation first then build my way up from there. Another important thing when laying a foundation is to make sure that the foundation I set will be used consistently through the project. Constant adjustments especially in large projects can affect further phases and how it functions. The main objective of this phase is to establish low-level system hooks to verify python runtime can safely control inputs and capture screen data across both macOS and Windows environments. I will establish two foundational tech stacks: Pyautogui and Pillow.

The primary challenge in phase 1 was figuring out how to programmatically move the mouse and take a screenshot after it moved to or landed in that specific input coordinates (x,y). This was solved by integrating two specialized Python libraries: PyAutoGUI (to programmatically drive system mouse inputs) and Pillow (to handle real-time frame capture and processing). 

Moving into the second phase, the next step is to give Saiga the ear to capture real-time audio and stream it to Muse Voice Transcribe 1.0 model to process into text.

### The Low-Level Execution Flow Matrix

The execution flow begins at the Software Layer, which leverages Python libraries to abstract complex actions into simple commands. Because Python cannot talk to hardware directly, these commands pass down to the OS API Layer. This layer acts as the system gatekeeper – requesting native permissions from Windows or macOS to interact with the system hooks, verifying accessibility access, and safely bridging the gap between your code and the underlying drivers. 

Once permission is granted, the request passes into the Kernel Layer, which acts as the core operating system bridge to communicate with system drivers. The kernel routes these instructions directly to the specific mouse and graphics drivers running in the system background. Finally, the Hardware Layer receives these low-level system commands, instantly translating the raw digital instructions into physical actions – updating the cursor position on your monitor and reading the raw pixels from your video memory grid.

<br>

| Layer | Component | Technical Execution Target |
| :--- | :--- | :--- |
| **Software Layer** | Python / PyAutoGUI / Pillow / os | Instantiates runtime context, manages image compression arrays, and abstracts UI requests into macro instructions. |
| **OS API Layer** | Win32 / CoreGraphics | Handles active OS gatekeeping protocols and ensures security verification handles match valid runtime threads. |
| **Kernel Layer** | Mouse & Graphics Drivers | Schedules thread execution blocks and interfaces directly with the background graphics pipeline architecture. |
| **Hardware Layer** | Mouse Cursor / VRAM Frame Buffer | Implements display coordinate hardware updates and reads structural canvas layout pixels in real time. |

<br>

#### Design

<img width="598" height="159" alt="Screenshot 2026-11-03 at 4 47 52 PM" src="https://github.com/user-attachments/assets/661cf9e0-63e1-419a-aa19-f712abec6777" />



</details>


<details>
<summary>🗣️ <b>Phase 2: Implementing WebSockets & Asyncio for Real-Time Audio-to-Text</b></summary>
<br>

Now that the software has performed a successful handshake with the low-level hardware, the objective of this phase is to give Saiga the ability to hear user requests in real-time. This works by implementing WebSockets, `asyncio`, and Meta's **Muse Voice Transcribe 1.0** to provide highly accurate, low-latency, and ultra-reliable fast audio-to-text transformation where continuous execution is vital.

### The Real-Time Network Challenge

The primary challenge in Phase 2 was minimizing the response-request cycle to conserve network bandwidth and eliminate processing latency. 

- **The WebSocket Edge:** To solve this, Saiga implements a native WebSocket layer. This provides a highly efficient, bidirectional ("two-way") connection rather than relying on traditional, high-overhead "one-way" HTTP protocols.
- **The Telephone Analogy:** This specific networking stack allows Muse Voice Transcribe 1.0 to send raw audio data chunks and receive structured text transcripts simultaneously without having to establish a brand-new handshake for every request. Think of it like a telephone call where both parties can speak and listen at the exact same time, compared to a clunky walkie-talkie that requires constant clicking to toggle half-duplex transmission.
- **Asyncio Concurrency:** Additionally, `asyncio` handles the core concurrency management. This ensures that the primary execution loop remains completely non-blocking while streaming live audio data packages in the background.

### The Audio Ingestion & Pipeline Path

The end-to-end processing pipeline handles real-time capture and streaming through three distinct phases:

1. **Hardware Capture:** An imported `sounddevice` library hooks into the system microphone, capturing raw physical sound waves and instantly transforming them into structured numerical data arrays that Python can read, manipulate, and compress.
2. **Buffer Management:** Raw data chunks are queued up inside an asynchronous data buffer loop (`asyncio.Queue`) at a blazing rate of **12 chunks per second**, keeping microphone ingestion isolated from execution blocks.
3. **Upstream Streaming & Filtering:** The active WebSocket tunnel routes these raw PCM audio chunks straight up to Meta's servers. The engine automatically filters out constant background room noise and microphone static hum. Saiga allows users to speak naturally at their own pace, terminating the stream gracefully only when speech pauses are detected.

#### Design

<img width="748" height="342" alt="Phase1 drawio" src="https://github.com/user-attachments/assets/ff7746d5-da0d-4bd6-a7ff-e3652594a3d4" />
<br>
<br>

</details>


<details>
<summary>👁️ <b>Phase 3: Multimodal Vision Pipeline through Base64 and OpenAI SDK with Muse Wonder 1.0</b></summary>
<br>

Seeing is just as important as hearing. Now that Saiga can convert real-time audio to text instantly, the next objective is to allow Saiga to see what is on the user's screen before taking action. This is done by capturing the user's screen state to dynamically navigate their virtual space. The critical components used to lay down the multimodal vision pipeline before integrating **Muse Wonder 1.0** are Base64 encoding and the OpenAI SDK structure. 

- **Base64 Processing:** This process converts raw binary image frames into standardized ASCII text strings that can be safely transferred across standard web protocols.
- **SDK Architecture:** Leveraging an OpenAI-compatible SDK layout allows for clean, plug-and-play functionality to manage model interaction cycles smoothly without rewriting core backend execution blocks—providing full architectural freedom.

### Solving the Vision & Coordinate Challenges

Interfacing a large multimodal model directly with OS-level click actions introduced several distinct system engineering challenges:

1. **The Hallucination & Screen Boundary Problem:** Model hallucination is a common problem in agentic workflows, especially when trying to accurately select a specific UI component via precise pixel coordinates. If the model is unaware of the maximum screen boundaries, click targets will easily drift.
2. **The Pixel Target Fix:** To resolve this, absolute bounding-box constraints were injected directly into the core system prompt within `vision_client.py`. This normalizes the display area onto a rigid grid space, preventing the vision model from guessing coordinates blindly and forcing hyper-accurate targeting.
3. **The Pacing & Latency Trade-off:** The process of capturing an image and converting it into a physical OS action can take a couple of seconds before hitting the low-level hardware hooks. The application must capture a high-quality frame to ensure accuracy, compress and encode it, stream it across the network, and wait for full visual reasoning to execute across the screen pixel grid. 

### *Architectural Optimization Reasoning*
While this vision pipeline introduces a high-latency step, it represents a conscious, calculated system optimization: it saves substantial API request costs, reduces unnecessary host computing resources, minimizes overall bandwidth, and prevents the backend server from lagging. It is far more efficient to process a high-quality frame once than to constantly spam cheap, low-resolution requests that fail to hit the exact UI element the user requested.

#### Design

<img width="732" height="114" alt="Phase3 drawio (3)" src="https://github.com/user-attachments/assets/890e5563-564f-4d0c-9795-80a114b65e37" />
<br>
<br>

</details>


---
*Developed as a solo indie project for the Meta Cerebral Valley Hackathon 2026. Built with a commitment to clean system architecture and meaningful digital accessibility.*
