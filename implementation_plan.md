# Implementation Plan - OpenAI Voice Upgrade

## Goal
Replace the failing browser-based voice tools with **OpenAI's Whisper (Speech-to-Text)** and **TTS (Text-to-Speech)**. This ensures high-quality Mongolian understanding and speaking.

## User Review Required
> [!IMPORTANT]
> This will consume OpenAI API credits for every second of audio processed. It is NOT free like the browser version, but it actually works for Mongolian.

## Proposed Changes

### Backend (main.py)
#### [MODIFY] [main.py](file:///c:/Users/nomad/receptionist-ai/main.py)
-   Import `UploadFile`.
-   Add `/talk` endpoint:
    1.  Receive `.webm` or `.wav` audio blob.
    2.  Save to temp file.
    3.  `client.audio.transcriptions.create` (Whisper) -> Get Text.
    4.  Send Text to Chat (Sarangoo) -> Get Response.
    5.  `client.audio.speech.create` (TTS) -> Get Audio.
    6.  Return JSON: `{ text: "...", audio: "base64..." }`.

### Frontend (static/index.html)
#### [MODIFY] [static/index.html](file:///c:/Users/nomad/receptionist-ai/static/index.html)
-   Remove `webkitSpeechRecognition` and `speechSynthesis`.
-   Implement `MediaRecorder`:
    -   Record microphone stream.
    -   Detect silence (volume threshold) to automatically stop recording and send.
    -   Or simpler: "Click to Start Speaking", "Click to Stop"? -> Let's try **Silence Detection** for natural flow.
-   Play back the returned audio blob.

## Verification Plan
1.  Reload server.
2.  Speak Mongolian.
3.  Verify the transcript is accurate (Whisper is very good).
4.  Verify the response audio sounds natural (OpenAI TTS).
