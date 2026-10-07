import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(
    page_title="Video to SRT Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Video to SRT Subtitle Generator")
st.caption("15–20 မိနစ်ဝန်းကျင် Video များအတွက် ပြုလုပ်ထားပါတယ်။")

@st.cache_resource
def load_model():
    return whisper.load_model("small")

video = st.file_uploader(
    "🎥 Video တင်ပါ",
    type=["mp4", "mkv", "mov", "avi"],
    help="15–20 မိနစ်ဝန်းကျင် Video ကို တင်နိုင်ပါတယ်။"
)

language = st.selectbox(
    "🌐 Video Language",
    ["auto", "my", "en", "th", "zh"],
    format_func=lambda x: {
        "auto": "Auto Detect",
        "my": "မြန်မာ",
        "en": "English",
        "th": "Thai",
        "zh": "Chinese"
    }[x]
)

model_size = st.selectbox(
    "🤖 AI Model",
    ["small", "base"],
    index=0,
    help="small = ပိုတိကျ၊ base = ပိုမြန်"
)

def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def create_srt(result):
    srt = ""
    for i, seg in enumerate(result["segments"]):
        srt += f"{i + 1}\n"
        srt += f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
        srt += seg["text"].strip() + "\n\n"
    return srt

if video:
    st.success(f"Video တင်ပြီးပါပြီ — {video.name}")

    if st.button("🚀 Generate SRT", type="primary"):
        path = None

        try:
            # Upload video to a temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(video.name)[1] or ".mp4"
            ) as file:
                file.write(video.getbuffer())
                path = file.name

            progress = st.progress(0)
            status = st.empty()

            status.info("🤖 Whisper AI Model ကို ပြင်ဆင်နေပါတယ်...")

            model = whisper.load_model(model_size)

            progress.progress(15)
            status.info("🎧 Video အသံကို ဖတ်ပြီး စာသားပြောင်းနေပါတယ်...")

            result = model.transcribe(
                path,
                language=None if language == "auto" else language,
                fp16=False,
                verbose=False
            )

            progress.progress(90)
            status.info("📝 SRT File ပြုလုပ်နေပါတယ်...")

            srt_text = create_srt(result)

            progress.progress(100)
            status.success("✅ SRT ထုတ်ပြီးပါပြီ!")

            base_name = os.path.splitext(video.name)[0]
            srt_filename = base_name + ".srt"

            st.download_button(
                label="⬇️ Download SRT",
                data=srt_text.encode("utf-8"),
                file_name=srt_filename,
                mime="application/x-subrip",
                type="primary"
            )

            with st.expander("📄 Transcript Preview"):
                st.text(srt_text[:5000])

        except Exception as e:
            st.error("❌ Video ကို Process လုပ်ရာမှာ Error ဖြစ်နေပါတယ်။")
            st.code(str(e))

        finally:
            if path and os.path.exists(path):
                os.remove(path)
else:
    st.info("👆 Video ဖိုင်ကို အပေါ်ကနေ တင်ပါ။")
