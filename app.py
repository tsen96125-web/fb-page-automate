import streamlit as st
import requests
import base64
import json
import os
from datetime import datetime
from PIL import Image
import io

# Raw spa data provided by user
ORIGINAL_SPA_DATA = """💥SUWASTHA MOBILE SPA💥

📌️ කෑගල්ල, මාවනැල්ල, රඹුක්කන අවට සිටින කාන්තා හා විවාහක යුවල් සදහා.


📌️ සේවා දායකයාට පහසු ස්තානයකට හෝ ලගම නගරයේ අප විසින් සූදානම් කර දෙන ආරක්ෂිත ස්ථානයකට පැමින සේවාව ලබා දීම.(home and room visit)

📌️අපගේ සේවාවන්
🔺ප්‍රධාන සේවාව:- 
🔸හිසේ සිට දෙපතුල දක්වා සම්භාහනය 
🔺අනෙකුත් සේවාවන්:-
🔸 හිස සදහා සම්භාහනය
🔸 බෙල්ලේ මාංශපේෂි සම්භාහනය
🔸 දෙඅත් සදහා සම්භාහනය
🔸 පියයුරැ විශේෂිත සමිභාහනය
🔸  කොන්ද සම්භාහනය
🔸 එල්ලා වැටුනු මාංශපේෂි සම්භාහනය
🔸 කලවා සම්භාහනය
🔸 දෙකකුල් සම්භාහනය
🔸 පියයුරු එල්ලා වැටීම වැලැක්වීමෙ හා විශාල කිරීමේ සම්භාහනය 
🔸පසු පෙදෙස එල්ලා වැටීම වැලැක්වීමෙ හා විශාල කිරීමේ සම්භාහනය 
🔸feeling massage සමග happy ending

📌️මෙම සියලුම සේවාවන් සුවිශේෂී පුහුණුවක් ලැබූ වසර 8ක පලපුරුද්දක් හිමි තෙරපිවරයෙකු මගින්  සිදුකරදෙනු ලැබේ. 

📌️දිනයක් හා වේලාවක් වෙන්කරවා ගැනිමට නොපමාව whats app කෙටි පණිවිඩයක් යොමු කරන්න. https://wa.me/94755495084"""

DEFAULT_PAGE_ID = "1132709063255625"
DEFAULT_ACCESS_TOKEN = "EAAVjpZAZBtIGABRnZC8aces9FQVITYejAZC4P3ZBO89NIKX2NQvZCdE9UTHGSD5LcNVzMYjl7nYknzTANvSeTtJWoReN0McYC2fpKgHH4XVBvlH7VSOwMbaidR4ChMlfZBuuKTPxtCzT8l469JMiVf04rB2xeTE5Lpip0n3nkRmh7eyFAL7hEQZCzDvnQ1ZBX2AF4E3sY"

# Page Configuration
st.set_page_config(
    page_title="Suwastha FB Automation",
    page_icon="💆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Dark Luxury Theme styling */
    .stApp {
        background: linear-gradient(135deg, #060814 0%, #0c0b1e 100%) !important;
        color: #f1f5f9 !important;
    }
    h1, h2, h3, h4, h5, h6, label, p, span {
        color: #f1f5f9 !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0b0d19 !important;
        border-right: 1px solid #1e293b !important;
    }
    /* Customize buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f43f5e 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 10px 20px rgba(244, 63, 94, 0.25) !important;
    }
    /* Card box effect */
    .glass-card {
        background: rgba(13, 16, 32, 0.75);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    /* Console log box */
    .console-box {
        font-family: monospace;
        background-color: #02040a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        max-height: 200px;
        overflow-y: auto;
        color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# Helper for Persistent History
HISTORY_FILE = "campaign_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history_list):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error saving history: {str(e)}")

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = load_history()

if "logs" not in st.session_state:
    st.session_state.logs = ["// System ready to launch. Customize specs and click the button."]

def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = "🚨 [ERROR]" if is_error else "ℹ️"
    st.session_state.logs.append(f"[{timestamp}] {prefix} {message}")

# --- SIDEBAR: Facebook & Key Settings ---
st.sidebar.markdown("### 🔑 System Integration")

# Gemini API Key integration (Supports Streamlit secrets as well)
default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
gemini_key_input = st.sidebar.text_input(
    "Gemini API Key", 
    value=default_api_key if 'default_api_key' in locals() else default_gemini_key, 
    type="password",
    help="Enter Gemini API key or set it up in Streamlit Secrets."
)

st.sidebar.markdown("---")
lock_settings = st.sidebar.checkbox("Lock Settings & Credentials", value=True)

# Persistent Page credentials in Session State
if "fb_page_id" not in st.session_state:
    st.session_state.fb_page_id = DEFAULT_PAGE_ID
if "fb_access_token" not in st.session_state:
    st.session_state.fb_access_token = DEFAULT_ACCESS_TOKEN

page_id_val = st.sidebar.text_input(
    "Facebook Page ID", 
    value=st.session_state.fb_page_id, 
    disabled=lock_settings
)
access_token_val = st.sidebar.text_area(
    "Page Access Token", 
    value=st.session_state.fb_access_token, 
    disabled=lock_settings,
    height=120
)

# Update state if unlocked and changed
if not lock_settings:
    st.session_state.fb_page_id = page_id_val
    st.session_state.fb_access_token = access_token_val

# --- MAIN APP LAYOUT ---
st.markdown('<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 25px;">'
            '<div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #f43f5e 0%, #f59e0b 100%); display: flex; align-items: center; justify-content: center; font-size: 24px;">💆</div>'
            '<div>'
            '<h1 style="margin: 0; font-size: 28px; font-weight: 800; background: linear-gradient(to right, #fbbf24, #f43f5e, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SUWASTHA AUTOMATION</h1>'
            '<p style="margin: 0; font-size: 13px; color: #94a3b8;">Direct Facebook Publishing & Persistent Archiving Studio</p>'
            '</div>'
            '</div>', unsafe_allow_html=True)

col1, col2 = st.columns([5, 7])

# LEFT COLUMN: Custom Specifications
with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Campaign Specifications")
    
    tone_option = st.selectbox(
        "Post Tone & Style (ලියන විලාසය)",
        [
            "Luxury & Premium (සුවිශේෂී සන්සුන් සුවතා විලාසය)",
            "Friendly & Informative (මිත්‍රශීලී සහ විස්තරාත්මක)",
            "Urgent Call-To-Action (සීමිත දීමනා සහිත විලාසය)"
        ]
    )
    
    lang_option = st.selectbox(
        "Sinhala Language (භාෂා විලාසය)",
        [
            "Pure Sinhala (පිරිසිදු සිංහල භාෂාවෙන්)",
            "Spoken/Singlish Mixed (මිශ්‍ර සරල ව්‍යවහාරික සිංහල)"
        ]
    )
    
    overlay_text = st.text_input("Text On Image (රූපය මත ඇති අකුරු)", value="Suwastha Mobile Spa")
    
    style_option = st.selectbox(
        "Visual Art Style (ඡායාරූපයේ විලාසය)",
        [
            "Cinematic Photo (සිනමාත්මක තාත්වික ඡායාරූපයක්)",
            "Luxury 3D Render (ත්‍රිමාණ සුඛෝපභෝගී සිතුවමක්)",
            "Minimalist Graphic (නවීන සරල චිත්‍රයක්)"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Master Action Button
    st.markdown('<br>', unsafe_allow_html=True)
    master_btn = st.button("🚀 Proceed to Post on Facebook")

# RIGHT COLUMN: Status Console & Live Persistent History
with col2:
    st.subheader("🖥️ Studio Control Center")
    
    # Live Console Logging Window
    st.markdown('<div class="console-box">', unsafe_allow_html=True)
    for log in reversed(st.session_state.logs):
        if "ERROR" in log:
            st.markdown(f'<span style="color: #f87171;">{log}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color: #cbd5e1;">{log}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    st.subheader("📂 පසුගිය ප්‍රචාරණ ලැයිස්තුව (Campaign History)")
    
    if len(st.session_state.history) == 0:
        st.info("තවමත් කිසිදු පෝස්ට් එකක් පල කර නොමැත. පෝස්ට් එකක් පලකල පසු විස්තර මෙහි ස්වයංක්‍රීයව සුරැකේ.")
    else:
        for idx, item in enumerate(st.session_state.history):
            with st.container():
                st.markdown('<div class="glass-card" style="padding: 15px;">', unsafe_allow_html=True)
                h_col1, h_col2 = st.columns([1, 2])
                
                with h_col1:
                    # Show cached base64 image
                    try:
                        img_bytes = base64.b64decode(item["image"].split(",")[1])
                        st.image(Image.open(io.BytesIO(img_bytes)), use_container_width=True)
                    except Exception as e:
                        st.warning("Image error")
                
                with h_col2:
                    st.markdown(f'**Post ID:** `{item["id"]}`')
                    st.caption(f'🕒 {item["timestamp"]}')
                    st.text_area("Post Text", value=item["text"], height=80, disabled=True, key=f"hist_txt_{idx}")
                    
                    # Metadata labels
                    st.markdown(f'<span style="font-size: 10px; background: #1e1b4b; padding: 4px 8px; border-radius: 4px;">Style: {item["specs"]["artStyle"]}</span> '
                                f'<span style="font-size: 10px; background: #1e1b4b; padding: 4px 8px; border-radius: 4px;">Tone: {item["specs"]["tone"]}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# --- WORKFLOW LOGIC ON BUTTON CLICK ---
if master_btn:
    if not gemini_key_input:
        st.error("කරුණාකර Gemini API Key එක ඇතුලත් කර සිටින්න.")
        add_log("Execution failed: Gemini API key is missing.", is_error=True)
    else:
        # Check for duplication signature
        tone_slug = "luxury" if "Luxury" in tone_option else ("friendly" if "Friendly" in tone_option else "urgent")
        lang_slug = "pure" if "Pure" in lang_option else "mix"
        art_slug = "cinematic" if "Cinematic" in style_option else ("3d" if "Luxury 3D" in style_option else "flat")
        overlay_clean = overlay_text.strip().lower()
        
        config_signature = f"{tone_slug}_{lang_slug}_{overlay_clean}_{art_slug}"
        
        is_duplicate = any(item.get("signature") == config_signature for item in st.session_state.history)
        
        if is_duplicate:
            st.error("ප්‍රතික්ෂේප කරන ලදී (Duplicate Prevented): මෙම සැකසුම්වලට සම්පූර්ණයෙන්ම සමාන පෝස්ට් එකක් මීට පෙර පළ කර ඇත.")
            add_log("Execution Blocked: Duplicate signature detected in persistent storage.", is_error=True)
        else:
            with st.spinner("Processing Pipeline (AI Copywriting + Graphic Design + FB Posting)..."):
                try:
                    # STEP 1: Gemini Copywriting Refinement
                    add_log("Starting copywriting generation via Gemini AI...")
                    
                    tone_instructions = ""
                    if tone_slug == "luxury":
                        tone_instructions = "Create a luxurious, premium spa advertising atmosphere. Highlight relaxing vibes, high standards of therapy, soothing details and respect."
                    elif tone_slug == "friendly":
                        tone_instructions = "Create a friendly, warm, clear, and highly welcoming social media introduction. Make it easy to read."
                    else:
                        tone_instructions = "Create a high-energy urgent call to action. Prompt them to message immediately because slots are limited, and highlight security and 8-year experience."

                    lang_instructions = ""
                    if lang_slug == "pure":
                        lang_instructions = "Use clean, correct, standard Sinhala language without standard English slang terms unless absolutely required."
                    else:
                        lang_instructions = "Write in everyday conversational Sinhala style. Incorporate direct English terms written in Sinhala phonetics for visual clarity (e.g. 'home visit', 'room visit', 'massage', 'whatsapp')."

                    system_prompt = f"""You are a professional social media campaign strategist from Sri Lanka. 
Write an elegant, engaging Facebook post in Sinhala based on raw spa details.
Guidelines:
- Tone Style: {tone_instructions}
- Language Variant: {lang_instructions}
- Keep details intact: Suwastha Mobile Spa, services in Kegalle, Mawanella, Rambukkana for ladies and couples, 8 years therapist, home/room visits, and WhatsApp: https://wa.me/94755495084
- End with exactly 15 highly viral, trending marketing hashtags related to beauty, wellness, massage, and spa.
Do not output any instructions or markdown code blocks inside the response, just return the raw text."""

                    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={gemini_key_input}"
                    gemini_payload = {
                        "contents": [{"parts": [{"text": ORIGINAL_SPA_DATA}]}],
                        "systemInstruction": {"parts": [{"text": system_prompt}]}
                    }
                    
                    gemini_res = requests.post(gemini_url, json=gemini_payload, timeout=30)
                    if gemini_res.status_code != 200:
                        raise Exception(f"Gemini API Error: {gemini_res.text}")
                    
                    polished_text = gemini_res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    add_log("Copywriting refinement successful.")

                    # STEP 2: Imagen Graphics Generation
                    add_log("Initiating cinematic asset rendering via Imagen 4...")
                    
                    style_directions = ""
                    if art_slug == "cinematic":
                        style_directions = "premium realistic photographic shot of luxurious tranquil spa setup. Elegant oil diffuser mist, candles, polished basalt hot stones, bamboo backdrop, warm golden luxury lighting."
                    elif art_slug == "3d":
                        style_directions = "luxury 3D graphic rendering of wellness elements. Elegant minimal shapes, smooth copper and amber light, abstract soft design."
                    else:
                        style_directions = "modern minimalist clean flat vector design. Relaxed vector curves, soothing colors, aesthetic graphic poster."

                    prompt_text = f"A beautiful background of: {style_directions}. Overlaid with sharp, legible, premium-looking graphic typographic text reading exactly '{overlay_text}' in the center. Advertising quality, 8k resolution, suitable for a luxurious brand banner."

                    imagen_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={gemini_key_input}"
                    imagen_payload = {
                        "instances": {"prompt": prompt_text},
                        "parameters": {"sampleCount": 1}
                    }
                    
                    imagen_res = requests.post(imagen_url, json=imagen_payload, timeout=45)
                    if imagen_res.status_code != 200:
                        raise Exception(f"Imagen API Error: {imagen_res.text}")
                    
                    base64_raw = imagen_res.json()["predictions"][0]["bytesBase64Encoded"]
                    base64_img = f"data:image/png;base64,{base64_raw}"
                    add_log("Graphic creation successful.")

                    # STEP 3: Upload directly to Facebook
                    add_log("Pushing assets directly onto Facebook Page feed...")
                    fb_url = f"https://graph.facebook.com/v18.0/{st.session_state.fb_page_id}/photos"
                    
                    # Convert base64 image data back to binary bytes for FB multipart upload
                    image_bytes = base64.b64decode(base64_raw)
                    
                    files = {
                        'source': ('suwastha-spa-campaign.png', image_bytes, 'image/png')
                    }
                    data = {
                        'message': polished_text,
                        'access_token': st.session_state.fb_access_token
                    }
                    
                    fb_res = requests.post(fb_url, files=files, data=data, timeout=30)
                    fb_res_json = fb_res.json()
                    
                    if fb_res.status_code != 200 or "error" in fb_res_json:
                        error_msg = fb_res_json.get("error", {}).get("message", "Unknown Facebook API error.")
                        raise Exception(error_msg)
                        
                    fb_post_id = fb_res_json.get("id", fb_res_json.get("post_id", "Success"))
                    add_log(f"Successfully posted on Facebook! Post ID: {fb_post_id}")

                    # STEP 4: Store in persistent local history & session state
                    new_campaign = {
                        "id": fb_post_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "text": polished_text,
                        "image": base64_img,
                        "signature": config_signature,
                        "specs": {
                            "tone": tone_slug,
                            "lang": lang_slug,
                            "overlayText": overlay_text,
                            "artStyle": art_slug
                        }
                    }
                    
                    st.session_state.history.insert(0, new_campaign)
                    save_history(st.session_state.history)
                    
                    st.success("සාර්ථකයි! පෝස්ට් එක සාර්ථකව පල කර ඇති අතර එහි පිටපතක් මෙවලමෙහි ඉතිහාසයට (History) සුරැකින.")
                    st.rerun()

                except Exception as ex:
                    st.error(f"පද්ධති දෝෂයකි: {str(ex)}")
                    add_log(f"Pipeline failure: {str(ex)}", is_error=True)
