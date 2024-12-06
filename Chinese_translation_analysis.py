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
3. The part of speech (e.g., noun, verb, adjective).
4. The meaning in {target_language}.
5. An example sentence using the word in the same context as the input sentence, translated into {target_language}.
6. Synonyms for the word, translated into {target_language}, if available.

Return the result as a JSON array, where each element is a dictionary with keys:
"word", "pinyin", "part_of_speech", "meaning", "example", and "synonyms".

Sentence: {text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return json.loads(response.choices[0].message["content"].strip())

# ฟังก์ชันหลัก
def main():
    st.title("Chinese Sentence Translation and Vocabulary Analysis")
    st.write("Easily translate Chinese sentences and learn key vocabulary with examples and synonyms.")

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
                try:
                    vocab_data = extract_vocab_with_pinyin(chinese_text, target_language)

                    if vocab_data:
                        st.subheader("Vocabulary Analysis with Examples and Synonyms")
                        
                        df = pd.DataFrame(vocab_data)
                        df = df[["word", "pinyin", "part_of_speech", "meaning", "example", "synonyms"]]
                        df['synonyms'] = df['synonyms'].apply(lambda x: ", ".join(x) if isinstance(x, list) and x else "N/A")
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
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please provide an API key and input text.")

if __name__ == "__main__":
    main()
