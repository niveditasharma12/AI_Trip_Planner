import streamlit as st
import requests
import datetime

BASE_URL = "http://localhost:8000"  # Backend endpoint

# =====================================================================
# 1. Page Configuration
# =====================================================================
st.set_page_config(
    page_title="🌍 AI Travel Planner",
    page_icon="🌍",
    layout="wide",  # Changed to wide layout for side-by-side view with sidebar
    initial_sidebar_state="expanded",
)

# =====================================================================
# 🎨 Travel Background Image & Custom UI Styling Integration
# =====================================================================
# High-resolution vintage map and travel aesthetic image URL
background_image_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1920"

st.markdown(
    f"""
    <style>
    /* 1. Inject background map image with a subtle light mask for crisp text contrast */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.82)), 
                          url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* 2. Force sidebar background transparency to blend into the map landscape seamlessly */
    [data-testid="stSidebar"] {{
        background-color: rgba(248, 250, 252, 0.88) !important;
        backdrop-filter: blur(4px);
        border-right: 1px solid rgba(226, 232, 240, 0.8);
    }}

    /* 3. Style chat containers to cleanly float above the background canvas */
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.6);
    }}

    /* 4. Smooth out status loader blocks overlay */
    div[data-testid="stStatusWidget"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
    }}

    /* 5. Clean, high-contrast dark typography across standard layout layers */
    h1, h2, h3, p, span, li, label, .stMarkdown {{
        color: #0f172a !important;
    }}
    
    /* Keep status message logs readable inside container wrappers */
    div[data-testid="stStatusWidget"] p, div[data-testid="stStatusWidget"] span {{
        color: #1e293b !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 2. App Styling Headers
# =====================================================================
st.title("🌍 Atriyo's Agentic Travel Planner")
st.caption("Powered by LangGraph, Groq (Llama 3.3), and Tavily Search")

# =====================================================================
# 3. Interactive Sidebar Filters
# =====================================================================
st.sidebar.header("⚙️ Trip Preferences")
st.sidebar.write("Refine your travel criteria before asking the agent:")

budget_tier = st.sidebar.select_slider(
    "Budget Category",
    options=["Backpacker / Budget", "Mid-Range", "Luxury"],
    value="Mid-Range"
)

days = st.sidebar.number_input("Duration (Days)", min_value=1, max_value=30, value=3)
travel_style = st.sidebar.multiselect(
    "Interests & Vibe",
    options=["Historical Places", "Food & Culinary", "Adventure & Trekking", "Beaches & Relaxation", "Shopping"],
    default=["Historical Places", "Food & Culinary"]
)

st.sidebar.divider()
if st.sidebar.button("🧹 Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# =====================================================================
# 4. Initialize Modern Chat Session State
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you plan your next trip? Mention your destination and I'll build an itinerary!"}
    ]

# =====================================================================
# 5. Render Historical Messages
# =====================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================================================
# 6. Modern Bottom Chat Input Bar
# =====================================================================
if user_input := st.chat_input("e.g., Plan a trip to Pune or Goa"):
    
    # Immediately display and save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Enrich prompt behind the scenes *only* if the history is empty or it's a new search
    # If the user is just saying "thank you", we pass their message naturally
    if any(keyword in user_input.lower() for keyword in ["thank", "yes", "no", "ok", "hello", "hi"]):
        enriched_prompt = user_input
    else:
        enriched_prompt = (
            f"{user_input}. "
            f"Keep the duration to exactly {days} days. "
            f"The budget category is {budget_tier}. "
            f"Focus heavily on: {', '.join(travel_style)}."
        )

    # Generate Assistant Bubble
    with st.chat_message("assistant"):
        with st.status("🤖 Travel Agent is thinking...", expanded=True) as status:
            try:
                status.write("🧠 Processing conversation...")
                
                # Pass the exact live message history payload to your backend
                payload = {
                    "messages": st.session_state.messages[:-1] + [{"role": "user", "content": enriched_prompt}]
                }
                
                response = requests.post(f"{BASE_URL}/query", json=payload)

                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer returned.")
                    status.update(label="✅ Response Generated!", state="complete", expanded=False)
                    
                    # Display the final answer immediately
                    st.markdown(answer)
                    
                    # Commit the exact answer to message history for the next chat turn
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Optional: Add download button if it looks like a long itinerary
                    if len(answer) > 300:
                        st.download_button(
                            label="📥 Download Plan (.md)",
                            data=answer,
                            file_name=f"itinerary.md",
                            mime="text/markdown"
                        )
                else:
                    status.update(label="❌ Generation Failed", state="error", expanded=True)
                    st.error(f"Execution Error: {response.text}")
                    
            except Exception as e:
                status.update(label="❌ Pipeline Offline", state="error", expanded=True)
                st.error(f"Backend Connection Error: {str(e)}")