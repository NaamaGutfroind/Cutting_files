import streamlit as st
from pydub import AudioSegment
import os
import zipfile
import io

# הגדרת נתיבים לשני הקבצים שנמצאים אצלך בתיקייה
current_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_exe = os.path.join(current_dir, "ffmpeg.exe")
ffprobe_exe = os.path.join(current_dir, "ffprobe.exe")

# עדכון הגדרות pydub שישתמשו בקבצים המקומיים בלבד
AudioSegment.converter = ffmpeg_exe
AudioSegment.ffprobe = ffprobe_exe

st.set_page_config(page_title="חותך אודיו", page_icon="✂️")
st.title("✂️ברוכים הבאים לחותך האודיו")

# בדיקה שהקבצים אכן מזוהים על ידי הקוד
if not os.path.exists(ffmpeg_exe) or not os.path.exists(ffprobe_exe):
    st.error("הקוד לא מוצא את ffmpeg.exe או ffprobe.exe בתיקייה.")
else:
    uploaded_file = st.file_uploader("העלו קובץ אודיו", type=['mp3', 'wav', 'm4a'])

    if uploaded_file:
        num_parts = st.number_input("לכמה חלקים לחתוך?", min_value=2, max_value=50, value=2)
        
        if st.button("בצע חיתוך"):
            try:
                with st.spinner("חותר את הקובץ... רק רגע..."):
                    audio = AudioSegment.from_file(uploaded_file)
                    part_length = len(audio) // num_parts
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for i in range(num_parts):
                            start = i * part_length
                            end = (i + 1) * part_length if i < num_parts - 1 else len(audio)
                            chunk = audio[start:end]
                            
                            chunk_io = io.BytesIO()
                            chunk.export(chunk_io, format="mp3")
                            zip_file.writestr(f"part_{i+1}.mp3", chunk_io.getvalue())
                    
                    st.success("החיתוך הסתיים בהצלחה!")
                    st.download_button("⬇️ הורד את כל החלקים (ZIP)", zip_buffer.getvalue(), "audio_parts.zip")
            except Exception as e:
                st.error(f"שגיאה בעיבוד: {e}")