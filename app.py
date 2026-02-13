import streamlit as st
from pydub import AudioSegment
import io
import zipfile

# הגדרות דף
st.set_page_config(page_title="חותך האודיו שלי", dir="rtl")
st.title("✂️ חותך אודיו אוטומטי")
st.write("העלי קובץ אודיו (MP3, WAV, M4A) והוא ייחתך לחלקים שווים")

# כאן החזרנו את התמיכה בכל סוגי הקבצים
uploaded_file = st.file_uploader("בחרי קובץ מהמחשב", type=['mp3', 'wav', 'm4a'])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    segment_length = st.number_input("אורך כל חלק (בשניות):", min_value=1, value=60)
    
    if st.button("חתוך והכן להורדה"):
        try:
            with st.spinner("מעבד... נא להמתין"):
                # קריאת הקובץ - pydub מזהה את הפורמט אוטומטית מהסיומת
                audio_data = io.BytesIO(uploaded_file.read())
                audio = AudioSegment.from_file(audio_data) 
                
                duration_ms = len(audio)
                segment_ms = segment_length * 1000
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for i, start_ms in enumerate(range(0, duration_ms, segment_ms)):
                        end_ms = min(start_ms + segment_ms, duration_ms)
                        chunk = audio[start_ms:end_ms]
                        
                        chunk_buffer = io.BytesIO()
                        # אנחנו מייצאים כ-MP3 כי זה הכי נוח להורדה, אבל הקלט יכול להיות כל דבר
                        chunk.export(chunk_buffer, format="mp3")
                        zf.writestr(f"part_{i+1}.mp3", chunk_buffer.getvalue())
                
                st.success("החיתוך הושלם בהצלחה!")
                st.download_button(
                    label="⬇️ לחצי כאן להורדת כל החלקים (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="cut_audio_files.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"אופס, קרתה שגיאה בעיבוד: {e}")
            st.info("טיפ: ודאי שהקובץ תקין ושהוא לא גדול מדי עבור השרת.")
