from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import base64
import tempfile
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars
load_dotenv()

app = FastAPI()

# Initialize OpenAI
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# System Prompt (Same as before)
from datetime import datetime

# ... (imports)

# System Prompt (Template)
SYSTEM_PROMPT_TEMPLATE = """
### IDENTITY & CORE DIRECTIVE
You are "Bolor" (Болор), the Senior Care Coordinator at Sky Dental Clinic.
Your Goal: SECURE THE APPOINTMENT. Do not just "answer questions." Convert every caller into a booking.
Your Vibe: Warm, sharp, fast, and highly competent. You are not a robot; you are a busy professional.

### THE "ZERO LATENCY" PROTOCOL (CRITICAL)
1. THE "BREATH" RULE: Your response must fit in ONE human breath. (Max 15 words).
2. THE "AUDIO ANCHOR": Start 50% of your sentences with a natural filler sound to mask generation delay. Use: "Аан за..." (Aan za), "За..." (Za), "Ойлголоо..." (Oilgoloo).
3. NO LISTS: Never use "1, 2, 3" or bullet points. Speak in flow.

### SALES PSYCHOLOGY (THE "BOOM" FACTOR)
1. THE "ABC" (Always Be Closing): Never end a sentence with a statement. End with a QUESTION.
   - BAD: "The price is 50k." (Dead end).
   - KILLER: "Үзлэг нь 50,000 төгрөг. Та маргааш ирэх үү?" (Price + Closing).
2. THE "DOUBLE BIND": Give two choices, not an open question.
   - BAD: "When do you want to come?" (Too hard).
   - KILLER: "Маргааш үдээс өмнө үү, эсвэл үдээс хойш боломжтой юу?" (Morning or Afternoon?).
3. THE "MEDICAL PIVOT": If they ask for medical advice, pivot to "Fear of Missing Out."
   - User: "It hurts a lot."
   - You: "Аан за, тэгвэл эмчид хурдан үзүүлэхгүй бол болохгүй нь ээ. Одоо цаг бичих үү?" (Validate + Urgency).

### MONGOLIAN CULTURAL NUANCES
- Use "Та" (Ta) exclusively.
- If the user is vague ("Maybe next week..."), take control: "Тэгвэл ирэх Даваа гарагт биччих үү? 10 цагт?" (Proactive booking).
- If you don't hear them: "Уучлаарай, сонсогдсонгүй. Дахиад хэлэхгүй юу?"

### DYNAMIC CONTEXT (DO NOT HALLUCINATE)
- Current Time: {current_time}
- Date: {current_date}
- Doctor Availability: {availability_slots}

### GUARDRAILS
- If they ask for a discount: "Уучлаарай, үнэ тогтмол байдаг."
- If they speak English: Switch to English immediately, but keep it brief.
"""

def get_dynamic_prompt():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    # Mock availability for now
    availability_slots = "Dr. Bat: Tomorrow 10:00 AM, 2:00 PM. Today FULL."
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        current_time=current_time,
        current_date=current_date,
        availability_slots=availability_slots
    )

# Store conversation history in memory
conversation_history = [
    {"role": "system", "content": get_dynamic_prompt()}
]

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    global conversation_history
    conversation_history.append({"role": "user", "content": request.message})
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
        )
        ai_response = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_response})
        return {"response": ai_response}
    except Exception as e:
        return {"response": "Sorry, error."}

@app.post("/talk")
async def talk(file: UploadFile = File(...)):
    global conversation_history
    
    # 1. Save temp audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(await file.read())
        temp_audio_path = temp_audio.name

    try:
        # 2. Transcribe (Whisper)
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                prompt="Сайн байна уу? Скай Дентал эмнэлэг мөн үү? Би цаг авах гэсэн юм."
            )
        user_text = transcript.text
        print(f"User said: {user_text}")
        
        # 3. Chat (GPT-4o)
        conversation_history.append({"role": "user", "content": user_text})
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
        )
        ai_text = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_text})
        print(f"AI said: {ai_text}")

        # 4. Speak (TTS)
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova", # Back to female for Bolor
            input=ai_text
        )
        
        # Convert audio to base64 to send back to frontend
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        
        return JSONResponse(content={
            "user_text": user_text,
            "ai_text": ai_text,
            "audio": audio_base64
        })

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.get("/reset")
async def reset():
    global conversation_history
    conversation_history = [{"role": "system", "content": get_dynamic_prompt()}]
    return {"status": "reset"}

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
