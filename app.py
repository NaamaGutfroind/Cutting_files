import streamlit as st
from pydub import AudioSegment
import os
import zipfile
import io

# --- הגדרת FFmpeg (נשאר בדיוק כמו ששלחת) ---
ffmpeg_exe = os.path.join(os.getcwd(), "ffmpeg.exe")
ffprobe_exe = os.path.join(os.getcwd(), "ffprobe.exe")

if os.path.exists(ffmpeg_exe):
    AudioSegment.converter = ffmpeg_exe
    AudioSegment.ffprobe = ffprobe_exe

st.set_page_config(page_title="חותך אודיו", page_icon="✂️")
st.title("✂️ ברוכים הבאים לחותך האודיו")

uploaded_file = st.file_uploader("העלו קובץ אודיו", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    num_parts = st.number_input("לכמה חלקים לחתוך?", min_value=2, max_value=50, value=2)
    
    if st.button("בצע חיתוך"):
        try:
            with st.spinner("חותך את הקובץ... רק רגע..."):
                # קריאת הקובץ ישירות מהזיכרון
                audio = AudioSegment.from_file(uploaded_file)
                part_length = len(audio) // num_parts
                
                # יצירת ה-ZIP בזיכרון הווירטואלי (במקום קובץ על הדיסק)
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for i in range(num_parts):
                        start = i * part_length
                        end = (i + 1) * part_length if i < num_parts - 1 else len(audio)
                        chunk = audio[start:end]
                        
                        # ייצוא החלק לזיכרון
                        chunk_io = io.BytesIO()
                        chunk.export(chunk_io, format="mp3")
                        zip_file.writestr(f"part_{i+1}.mp3", chunk_io.getvalue())
                
                # הכנה להורדה
                st.success("החיתוך הסתיים בהצלחה!")
                st.download_button(
                    label="⬇️ הורד את כל החלקים (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="audio_parts.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"שגיאה בעיבוד: {e}")
