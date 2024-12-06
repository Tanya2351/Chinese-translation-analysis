import streamlit as st
import pandas as pd
import openai
import json

# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

# ฟังก์ชันแปลภาษาจีน
def translate_text(text, target_language="th"):
    prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message["content"].strip()

# ฟังก์ชันแยกคำศัพท์พร้อมตัวอย่างการใช้งานและคำพ้องความหมาย
def extract_vocab_with_pinyin(text, target_language="th"):
    prompt = f"""
Analyze the following Chinese sentence. Extract important words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The meaning in {target_language}.
4. The part of speech (e.g., noun, verb, adjective).
5. An example sentence using the word in the same context as the input sentence.
6. Synonyms for the word, if available.

Return the result as a JSON array, where each element is a dictionary with keys:
"word", "pinyin", "meaning", "part_of_speech", "example", and "synonyms".

Sentence: {text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    # แปลงข้อความ JSON ที่ได้จาก API เป็นโครงสร้างข้อมูล Python
    vocab_data = json.loads(response.choices[0].message["content"].strip())
    return vocab_data

# ฟังก์ชันหลัก
def main():
    st.title("Chinese Sentence Translation and Vocabulary Analysis")
    st.write("Translate and analyze Chinese sentences with detailed vocabulary breakdown.")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language for translation and vocabulary:", ["th", "en"])

    if st.button("Translate and Analyze"):
        if api_key and chinese_text:
            with st.spinner("Processing..."):
                # แปลข้อความ
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)

                # วิเคราะห์คำศัพท์พร้อมตัวอย่างการใช้งานและคำพ้องความหมาย
                vocab_data = extract_vocab_with_pinyin(chinese_text, target_language)

                if vocab_data:
                    st.subheader("Vocabulary Analysis with Examples and Synonyms")
                    
                    # สร้าง DataFrame จากผลลัพธ์จริง
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
                    st.error("No vocabulary data extracted. Please try again with a different sentence.")
        else:
            st.error("Please provide an API key and input text.")

if __name__ == "__main__":
    main()
