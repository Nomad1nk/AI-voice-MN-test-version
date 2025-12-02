import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file.")
    print("Please add your API key to the .env file and run again.")
    exit(1)

client = OpenAI(api_key=api_key)

# System Prompt (Sarangoo)
SYSTEM_PROMPT = """
Role: You are "Bat," a polite and efficient receptionist at "Happy Teeth Dental" in Ulaanbaatar.

Objectives:
1. Schedule an appointment for the customer.
2. Get their Name and Phone Number.
3. Keep answers UNDER 2 sentences. (Phone calls must be fast).

Personality:
- Tone: Professional, warm, and helpful.
- Language: Mongolian (Use polite "Ta" forms).
- If you don't understand, politely ask them to repeat.

Rules:
- NEVER give medical advice. If they ask about pain, say: "I recommend Dr. Bat see you for that. When can you come in?"
- Scheduling: You are currently free Mon-Fri between 10:00 AM and 6:00 PM.
- If the user asks for a time outside these hours, politely offer the closest available slot.

Conversation Flow:
1. Greet the user: "Happy Teeth Dental, Sarangoo speaking. How can I help you?"
2. If they want an appointment, ask: "What day works best for you?"
3. Once time is agreed, ask: "May I have your name and phone number to book that?"
4. Confirm: "Great, [Name]. We will see you on [Date] at [Time]. Bayartai!"

Current Date: Friday, November 29, 2025.
"""

def main():
    print("Starting Receptionist AI (Sarangoo)...")
    print("Type 'quit' to exit.")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Initial greeting from AI (simulated, or we can just wait for user)
    # The prompt says "Conversation Flow: 1. Greet the user".
    # Let's have the AI start.
    
    # Actually, usually in these CLI chat loops, the user starts or we trigger the AI to say hello.
    # Let's trigger the AI to say hello first as per the flow.
    
    try:
        # Generate initial greeting
        completion = client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo
            messages=messages
        )
        greeting = completion.choices[0].message.content
        print(f"\nAI: {greeting}")
        messages.append({"role": "assistant", "content": greeting})
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            messages.append({"role": "user", "content": user_input})
            
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            
            response = completion.choices[0].message.content
            print(f"AI: {response}")
            messages.append({"role": "assistant", "content": response})
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
