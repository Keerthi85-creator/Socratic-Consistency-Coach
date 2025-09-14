# gemini_image.py
from google import genai
import os

def generate_insight_image(insight_text, api_key=None, model="image-bison-001", mock=False):
    """
    model: pick a model name available to your account; example names vary.
    Returns: a public URL or base64 data depending on the response.
    """
    if mock:
        # return a placeholder image URL (you can put some stock url or local asset)
        return "https://via.placeholder.com/1024x1024.png?text=Insight+Card+Placeholder"

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

    prompt = (
        f"A simple, minimalist, and beautiful badge or card that visually represents the concept: '{insight_text}'. "
        "Style: vector art, minimalist, clean graphic design badge, modern typography, flat shapes, calm colors."
    )

    # sample call using image generation API (SDK's image API)
    img = genai.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024",
        # you can pass other params like guidance
    )
    # The SDK response often contains a `uri` or `b64` depending on config.
    # Here we try to pull a URL or binary.
    if hasattr(img, "data") and len(img.data) > 0:
        item = img.data[0]
        # item may have 'uri' or 'b64' or 'image' fields depending on SDK version
        if "uri" in item:
            return item["uri"]
        if "b64" in item:
            import base64, tempfile
            b = base64.b64decode(item["b64"])
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tf.write(b); tf.flush()
            return tf.name
    # fallback placeholder
    return "https://via.placeholder.com/1024x1024.png?text=Insight+Card+Fallback"
