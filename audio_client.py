import asyncio
import json
import os
import sys
import uuid
import sounddevice as sd
import websockets
from dotenv import load_dotenv

# Automatically load system variables from our local hidden .env block
load_dotenv()

# Global fallback assignment to catch missing environment parameters
if "MODEL_API_KEY" not in os.environ:
    os.environ["MODEL_API_KEY"] = os.environ.get("META_API_KEY", "")
if "ASR_MODEL" not in os.environ:
    os.environ["ASR_MODEL"] = "muse-voice-transcribe-1.0"

async def _stream_audio_to_meta_websocket() -> str:
    """Internal async task that streams mic bytes dynamically and auto-stops on voice silence."""
    api_key = os.environ.get("MODEL_API_KEY")
    model_id = os.environ.get("ASR_MODEL")
    
    if not api_key or len(api_key) < 10:
        raise ValueError("Missing full secret MODEL_API_KEY inside your local .env configuration!")

    session_id = f"mic-{uuid.uuid4()}"
    uri = f"wss://api.meta.ai/v1/asr/realtime?sessionId={session_id}"
    
    rate = 24000
    frame_samples = rate * 80 // 1000  # 80ms chunk intervals
    
    # DYNAMIC SILENCE CONFIGURATION
    SILENCE_THRESHOLD = 2500   # Amplitude threshold (adjust slightly if your mic is in a noisy room)
    SILENCE_DURATION = 1.8    # Stop listening after exactly 1.8 seconds of unbroken pause
    MAX_RECORD_TIMEOUT = 45.0 # Absolute safety cutoff so it doesn't stream forever if background noise is loud
    
    final_transcript = ""

    async with websockets.connect(uri, open_timeout=30) as ws:
        # Step 1: Send configuration header frame
        await ws.send(
            json.dumps(
                {
                    "authorization": {"accessToken": f"Bearer {api_key}"},
                    "audioEncoding": "PCM_24KHZ",
                    "model": model_id,
                    "mode": "PUSH_TO_TALK",
                    "partialMode": "CUMULATIVE",
                    "emitAudioProgress": False,
                }
            )
        )

        handshake = json.loads(await ws.recv())
        if "sessionId" not in handshake:
            raise RuntimeError(f"Handshake failed: {handshake}")
            
        print(f"\n[Saiga Listening] Speak at your own pace... (Auto-stops when you pause)")

        loop = asyncio.get_running_loop()
        audio_queue: asyncio.Queue[bytes] = asyncio.Queue()

        def on_audio(indata, frames, time_info, status):
            if status:
                print(status, file=sys.stderr)
            loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

        async def receive_events() -> None:
            nonlocal final_transcript
            previous_length = 0
            async for message in ws:
                if isinstance(message, bytes):
                    continue

                event = json.loads(message)
                if event.get("type") == "error":
                    raise RuntimeError(event["message"])
                if event.get("type") != "transcript":
                    continue

                transcript = event["transcript"]
                padding = " " * max(0, previous_length - len(transcript))
                end = "\n" if event.get("final") else "\r"
                print(f"👉 Real-time Translation: {transcript}{padding}", end=end, flush=True)
                previous_length = len(transcript)
                
                if event.get("final") or len(transcript) > len(final_transcript):
                    final_transcript = transcript

        receiver = asyncio.create_task(receive_events())

        # Track silent segments dynamically
        silence_accumulator = 0.0
        chunk_seconds = 80 / 1000.0  # Each chunk represents 0.08 seconds of time
        start_time = loop.time()
        
        # FIXED: Safety delay to prevent picking up immediate speaker echo or mic hardware pops
        PRE_LISTEN_DELAY = 1.0  

        # Step 2: Open hardware audio device buffer stream mapping
        with sd.RawInputStream(
            samplerate=rate,
            channels=1,
            dtype="int16",
            blocksize=frame_samples,
            callback=on_audio,
        ):
            while True:
                audio_bytes = await audio_queue.get()
                await ws.send(audio_bytes)
                
                elapsed_time = loop.time() - start_time
                
                # FIXED: Skip volume analysis during the initial pre-listen delay window
                if elapsed_time < PRE_LISTEN_DELAY:
                    continue
                
                # Natively decode the binary byte buffer into signed 16-bit numeric values
                # Every 2 bytes forms one int16 sample
                samples = []
                for i in range(0, len(audio_bytes), 2):
                    if i + 1 < len(audio_bytes):
                        # Construct a signed integer out of little-endian bytes
                        sample = int.from_bytes(audio_bytes[i:i+2], byteorder='little', signed=True)
                        samples.append(abs(sample))
                
                max_amplitude = max(samples) if samples else 0
                
                # Check if the audio chunk volume falls below our silent baseline
                if max_amplitude < SILENCE_THRESHOLD:
                    silence_accumulator += chunk_seconds
                else:
                    silence_accumulator = 0.0  # Reset the clock entirely because voice was detected
                
                # FIXED: Only check for silence cutoff after the pre-listen safety window passes
                if silence_accumulator >= SILENCE_DURATION and elapsed_time > (PRE_LISTEN_DELAY + 1.0):
                    print("\n[Silence Detected] Finalizing transcription context...")
                    break
                    
                if elapsed_time > MAX_RECORD_TIMEOUT:
                    print("\n[Max Safety Timeout] Processing capture stream baseline...")
                    break

        while not audio_queue.empty():
            await ws.send(audio_queue.get_nowait())

        # Step 3: Close connection gracefully
        await ws.send(json.dumps({"type": "endStream"}))
        await receiver
        
    return final_transcript.strip()

def listen_for_command():
    """Synchronous interface wrapper that executes the underlying asynchronous streaming loop cleanly."""
    try:
        return asyncio.run(_stream_audio_to_meta_websocket())
    except Exception as e:
        print(f"\n[Meta Voice API Exception] Handshake failed or disconnected: {e}")
        return ""

if __name__ == "__main__":
    print("--- Step 5: Verifying Official Meta Streaming Voice Pipeline ---")
    listen_for_command()
