import os
import streamlit as st
import google.generativeai as genai
from insight_card import generate_insight_card

# Configure Streamlit page
st.set_page_config(page_title="Socratic Consistency Coach", layout="centered")

# Configure Gemini with API key from env or Streamlit secrets
GEMINI_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY"))
if not GEMINI_API_KEY:
    st.error("⚠️ Please set GOOGLE_API_KEY in Streamlit secrets or environment variables. See README for details.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# App Header
st.title("🧠 Socratic Consistency Coach")
st.write("A guided reflection tool powered by **Google Gemini Pro** that helps you discover your own solutions through thoughtful questioning.")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "aha" not in st.session_state:
    st.session_state.aha = False
if "insight" not in st.session_state:
    st.session_state.insight = None
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# Start form - only show if chat hasn't started
if not st.session_state.chat_started:
    st.header("What's your consistency challenge?")
    with st.form("initial_form"):
        user_problem = st.text_area(
            "Describe your current challenge with consistency:", 
            placeholder="I can't stay consistent with...",
            height=120
        )
        submit = st.form_submit_button("🚀 Start Coaching Session")

    if submit and user_problem.strip():
        st.session_state.history = []
        st.session_state.aha = False
        st.session_state.insight = None
        st.session_state.chat_started = True

        # Add user's initial problem to history
        st.session_state.history.append({"role": "user", "content": user_problem.strip()})

        # Generate first coaching question
        prompt = f"""You are an AI Socratic Coach for consistency. Your purpose is to help a student uncover their own gaps and blockers, not to provide direct advice. 

Your role:
- Ask ONE thoughtful, open-ended question at a time
- Guide them through self-reflection
- Never provide direct solutions or advice
- Help them discover their own insights
- The conversation should feel like guided self-discovery

The student's consistency challenge is: {user_problem}

Ask your first reflective question to help them explore this challenge deeper."""

        try:
            response = model.generate_content(prompt)
            st.session_state.history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
        
        st.rerun()

# Show conversation if chat has started
if st.session_state.chat_started:
    st.header("💬 Coaching Conversation")
    
    # Display conversation history
    for i, msg in enumerate(st.session_state.history):
        if msg["role"] == "user":
            st.markdown(f"**🙋 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Coach:** {msg['content']}")
        
        # Add some spacing between messages
        if i < len(st.session_state.history) - 1:
            st.markdown("---")

    # Only show reply section if there's at least one coach response and no aha moment yet
    if len(st.session_state.history) > 1 and not st.session_state.aha:
        st.markdown("---")
        st.header("🤔 Your Response")
        
        reply = st.text_area(
            "Respond to the coach's question:",
            placeholder="Share your thoughts... (Hint: Try phrases like 'I get it!', 'My blocker is...', or 'My small step is...' when you have an insight)",
            key="reply_box",
            height=120,
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            send_reply = st.button("💬 Send Reply", use_container_width=True)
        
        if send_reply and reply.strip():
            st.session_state.history.append({"role": "user", "content": reply.strip()})

            # Enhanced aha detection
            low = reply.lower()
            aha_triggers = [
                "i get it", "aha", "my small step", "i understand", "my blocker",
                "i realize", "now i see", "the issue is", "i need to", "breakthrough"
            ]
            
            if any(trigger in low for trigger in aha_triggers):
                st.session_state.aha = True
                st.session_state.insight = reply.strip()
                st.rerun()
            else:
                # Continue the Socratic questioning
                conversation = "\n".join([
                    f"{h['role'].title()}: {h['content']}" 
                    for h in st.session_state.history
                ])
                
                prompt = f"""Continue as a Socratic Coach for consistency. 
                
Your role:
- Ask ONE reflective, open-ended question at a time
- Guide them deeper into self-reflection
- Never provide direct solutions or advice
- Help them uncover their own insights about their consistency challenges

Conversation so far:
{conversation}

Ask your next thoughtful question to help them explore further."""

                try:
                    response = model.generate_content(prompt)
                    st.session_state.history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                
                st.rerun()

    # Show aha moment celebration
    if st.session_state.aha:
        st.balloons()
        st.success("🎉 Breakthrough detected! You've had an insight!")
        
        with st.container():
            st.subheader("✨ Your Insight:")
            st.info(st.session_state.insight)
            
            # Try to generate insight card if function is available
            try:
                st.write("🎨 Generating your personalized Insight Card...")
                img = generate_insight_card(st.session_state.insight)
                if img:
                    st.image(img, caption="Your Personalized Insight Card")
                else:
                    st.info("💡 In a full version, this would generate a beautiful visual Insight Card. For now, your insight is captured above!")
            except Exception as e:
                st.info("💡 Your insight has been captured! In a full version, this would generate a beautiful visual Insight Card.")
        
        # Option to start a new session
        st.markdown("---")
        if st.button("🔄 Start New Coaching Session"):
            # Reset all session state
            st.session_state.history = []
            st.session_state.aha = False
            st.session_state.insight = None
            st.session_state.chat_started = False
            st.rerun()

# Sidebar with tips and debug info
with st.sidebar:
    st.header("💡 Tips")
    st.write("**How it works:**")
    st.write("1. Share your consistency challenge")
    st.write("2. Answer the coach's reflective questions honestly")
    st.write("3. Keep exploring until you have an 'aha!' moment")
    
    st.write("**Trigger breakthrough detection by using phrases like:**")
    st.write("- 'I get it!'")
    st.write("- 'My blocker is...'")
    st.write("- 'My small step is...'")
    st.write("- 'I realize...'")
    st.write("- 'Now I see...'")
    
    if st.session_state.chat_started:
        st.markdown("---")
        st.header("🔧 Session Info")
        st.write(f"**Messages:** {len(st.session_state.history)}")
        st.write(f"**Breakthrough:** {'Yes! 🎉' if st.session_state.aha else 'Not yet'}")
        
        if st.button("🗑️ Clear Session"):
            st.session_state.history = []
            st.session_state.aha = False
            st.session_state.insight = None
            st.session_state.chat_started = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown("*Powered by Google Gemini • Built with Streamlit*")
