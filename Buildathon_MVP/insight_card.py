import google.generativeai as genai

def generate_insight_card(user_insight: str):
    try:
        vision_model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Generate a minimalist, elegant, and modern visual badge that represents "
            f"the concept of '{user_insight}'. Make it feel like an achievement badge, "
            f"simple, and visually appealing. Use vector-style art."
        )
        result = vision_model.generate_content(prompt, stream=False)
        # Return first image if exists
        if result.candidates and result.candidates[0].content.parts[0].inline_data.data:
            return result.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print("Insight Card Error:", e)
        return None
