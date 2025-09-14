# gemini_engine.py
from google import genai
import os

class GeminiSocraticEngine:
    def __init__(self, api_key=None, model="gemini-pro", mock=False):
        """
        model: choose appropriate Gemini model available to your key (e.g., "gemini-pro", "gemini-1.5-mini" etc).
        mock: if True, returns canned responses for offline testing.
        """
        self.mock = mock
        if not mock:
            # Set API key for google-genai SDK
            if api_key:
                os.environ["GOOGLE_API_KEY"] = api_key
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.system_prompt = (
            "You are an AI Socratic Coach for consistency. Your goal is to help a student "
            "uncover their own blockers and solutions, not to give direct advice. "
            "Ask one reflective, open-ended question at a time. Do not provide a solution or next steps."
        )
        self.model = model

    def ask_next_question(self, history):
        if self.mock:
            # Very small deterministic fallback for demo
            return "What usually stops you after a week?"
        # Build the conversation messages
        # google-genai uses `genai.chat` interface
        messages = [{"role": "system", "content": self.system_prompt}]
        for h in history:
            role = h['role']
            # map roles to google roles if needed
            messages.append({"role": role, "content": h['content']})

        response = genai.chat.create(
            model=self.model,
            messages=messages,
            temperature=0.9,
            max_output_tokens=200
        )
        # The SDK returns `output` with candidates; get text
        text = response.output[0].content[0].text
        # ensure ends with a question
        if not text.strip().endswith('?'):
            text = text.strip()
            if not text.endswith('?'):
                text += ' ?'
        return text.strip()

    def extract_insight(self, user_reply, history):
        # Keep same simple heuristic as before
        import re
        m = re.search(r':\s*(.+)$', user_reply)
        if m:
            return m.group(1).strip()
        parts = user_reply.strip().split('.')
        last = parts[-1].strip()
        words = last.split()
        return ' '.join(words[-6:]) if len(words) > 6 else last or user_reply.strip()
