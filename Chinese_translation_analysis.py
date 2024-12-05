import streamlit as st
import pandas as pd
import openai

# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

# ฟังก์ชันแปลภาษาจีน
def translate_text(text, target_language="th"):
    prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# ฟังก์ชันแยกคำศัพท์พร้อมพินอิน
def extract_vocab_with_pinyin(text):
    prompt = f"""
Analyze the following Chinese sentence. Extract important words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The meaning in English.
4. The part of speech (e.g., noun, verb, adjective).
5. An example usage of the word.

Sentence: {text}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300
    )
    return response.choices[0].text.strip()

# ฟังก์ชันหลัก
def main():
    st.title("Translate and Understand Chinese Sentences")
    st.write("Easily translate and analyze Chinese text")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language:", ["th", "en"])
    
    if st.button("Translate and Analyze"):
        if api_key and chinese_text:
            with st.spinner("Processing..."):
                # แปลข้อความ
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)
                
                # วิเคราะห์คำศัพท์พร้อมพินอิน
                vocab_analysis = extract_vocab_with_pinyin(chinese_text)
                st.subheader("Vocabulary Analysis with Pinyin")
                st.text(vocab_analysis)
                
                # ตัวอย่างตารางคำศัพท์
                st.subheader("Sample Vocabulary Table")
                vocab_data = {
                    "Word": ["我", "喜欢", "学习", "中文"],
                    "Pinyin": ["wǒ", "xǐ huān", "xué xí", "zhōng wén"],
                    "Meaning": ["I", "like", "learn", "Chinese"],
                    "Part of Speech": ["Pronoun", "Verb", "Verb", "Noun"],
                    "Example": [
                        "我很高兴。(I am happy.)",
                        "我喜欢听音乐。(I like listening to music.)",
                        "他学习得很努力。(He studies hard.)",
                        "你会说中文吗？(Can you speak Chinese?)"
                    ]
                }
                df = pd.DataFrame(vocab_data)
                st.dataframe(df)

                # ดาวน์โหลดผลลัพธ์
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="chinese_analysis_with_pinyin.csv",
                    mime="text/csv",
                )
        else:
            st.error("Please provide an API key and input text.")

if __name__ == "__main__":
    main()